from abc import ABC

import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import numpy as np
from plotly.graph_objects import Figure
import pandas as pd
import pickle
from urllib.request import urlopen

from ..mixins import SimulationTransformerMixin
from ..static_elements import brand, footer
from ..configuration import DATA_REPO_URL_RAW


class ValidationData(ABC):
    MAX_TIME = 120

    @staticmethod
    def get_csv_from_repo(file):
        return pd.read_csv(f"{DATA_REPO_URL_RAW}/{file}")

    @staticmethod
    def get_pickle_from_repo(file):
        url = DATA_REPO_URL_RAW + '/validation/' + file + '.pkl'

        with urlopen(url) as f:
            df = pickle.load(f)

        return df

    @staticmethod
    def transform_covid(df):
        # transform dates
        df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")
        df = df.sort_values('date').reset_index(drop=True)

        num_cols = ['tot_cases', 'new_cases']

        col_transform = {c: 'float32' for c in num_cols if c in df.columns}

        for c in col_transform:
            df[c] = df[c].apply(lambda x: x.replace(',', '') if type(x) == str else x, 1)

        df.replace('NaN', np.NaN, inplace=True)

        # transform numbers
        df = df.astype(col_transform)

        return df

    @classmethod
    def get_data_after_date(cls, df, date: str):
        df = df[df['date'] >= np.datetime64(date)].copy()
        df.reset_index(drop=True, inplace=True)

        start_date = df.loc[0, 'date'].date()
        df['date'] = df['date'].apply(lambda x: (x.date() - start_date).days)

        df = df.loc[df['date'] <= cls.MAX_TIME, :].copy()

        return df

    @staticmethod
    def calc_new_cases(df):
        first_val = 0
        df['new_cases'] = df['tot_cases'].diff().fillna(first_val).values.tolist()

        return df.copy()

    @staticmethod
    def make_counts_relative(df, population):
        df['new_cases'] = [c / population for c in df['new_cases'].values.tolist()]
        df['tot_cases'] = [c / population for c in df['tot_cases'].values.tolist()]
        return df


class EmpiricalData(ValidationData):
    US_FILE = 'validation/case-data/us_covid_count_by_state.csv'
    POP_FILE = 'validation/case-data/us_population_by_state.csv'

    def __init__(self):
        super().__init__()
        self.covid_us = self.get_csv_from_repo(self.US_FILE)
        self.pop_map = self.make_state_population()
        self.first_wave_map = self.make_first_wave_map()
        self.all_states = self.make_all_states()

    @classmethod
    def make_state_population(cls):
        df = cls.get_csv_from_repo(cls.POP_FILE)

        df['population'] = df['population'].apply(
            lambda x: x.replace(',', '') if type(x) == str else x, 1)

        df = df.astype({'population': 'float32'})

        records = df.drop('state_name', 1).dropna().to_dict('records')

        return {x['state']: x['population'] for x in records}

    def make_first_wave_map(self, threshold=0.001):
        """
        First date when tot_cases / population > 0.001 for each state.
        """
        df = self.transform_covid(self.covid_us)

        first_wave_map = {}

        for state in df.state.unique():
            subset = df[df.state == state].sort_values('date')
            if state not in self.pop_map:
                continue
            threshold_cases = self.pop_map[state] * threshold
            date = subset[subset.tot_cases >= threshold_cases].iloc[0].date
            first_wave_map[state] = date.strftime("%Y-%m-%d")

        return first_wave_map

    @staticmethod
    def extract_region(df, region_filter):
        region_col = region_filter['column']
        region_val = region_filter['value']
        df_out = df[df[region_col] == region_val].copy()
        df_out.reset_index(drop=True, inplace=True)
        return df_out

    def make_state_covid(self, state):

        start_date = self.first_wave_map[state]

        df = self.transform_covid(self.covid_us)

        state_filter = {'column': 'state', 'value': state}
        df_state = self.extract_region(df, state_filter)

        df_state = self.get_data_after_date(df_state, start_date)

        pop = self.pop_map[state]
        df_state = self.make_counts_relative(df_state, pop)

        return df_state

    def make_all_states(self):
        dfs = []

        for state in self.pop_map:
            if state == 'NYC':
                continue
            else:
                dfs.append(self.make_state_covid(state))

        return pd.concat(dfs)


class ModelledData(ValidationData, SimulationTransformerMixin):

    VALIDATION_FILES = [
        {'name': 'v_seir_mobility_pre', 'title': 'SEIR, M (Pre)'},
        {'name': 'v_seirq_25_mobility_pre', 'title': 'SEIR_Q (p=0.25), M (Pre)'},
        {'name': 'v_seirq_50_mobility_pre', 'title': 'SEIR_Q (p=0.5), M (Pre)'},
        {'name': 'v_seirq_75_mobility_pre', 'title': 'SEIR_Q (p=0.75), M (Pre)'},
        {'name': 'v_seir_mobility_post', 'title': 'SEIR, M (Post)'},
        {'name': 'v_seirq_25_mobility_post', 'title': 'SEIR_Q (p=0.25), M (Post)'},
        {'name': 'v_seirq_50_mobility_post', 'title': 'SEIR_Q (p=0.5), M (Post)'},
        {'name': 'v_seirq_75_mobility_post', 'title': 'SEIR_Q (p=0.75), M (Post)'},
    ]

    def __init__(self):
        super().__init__()
        self.results = []
        self.make_validation_data()

    def get_result(self, name):
        for r in self.results:
            if r['name'] == name:
                return r
        return None

    @property
    def valid_names(self):
        return [x['name'] for x in self.VALIDATION_FILES]

    def make_validation_data(self):
        for v in self.VALIDATION_FILES:
            r = v.copy()
            r['data'] = self._get_wide(v['name'], self.MAX_TIME)
            self.results.append(r)

    @classmethod
    def _get_wide(cls, name, max_time):
        # get data frame
        df = cls.get_pickle_from_repo(name)

        # transform
        df = df[df.time <= max_time]

        df = cls.fill_experiment_length_gap(df, delta=1)

        grouped = cls.df_group_mean(df)
        wide = grouped.pivot(index=['time'], columns=['compartment'], values='value')
        wide.reset_index(inplace=True)

        # calc new cases
        first_val = 0
        new_cases = (wide['S'].diff().fillna(first_val) * (-1)).values.tolist()
        new_cases = [int(x) if np.isclose(x, 0) else x for x in new_cases]
        wide['new_cases'] = new_cases

        # calc total cases
        wide['tot_cases'] = wide['E'] + wide['I'] + wide['R']

        return wide


modelled = ModelledData()
empirical = EmpiricalData()


def make_validation_graph(name, y):
    fig1 = px.line(empirical.all_states, x='date', y=y, color='state')
    fig1.update_traces(opacity=0.2, showlegend=False)

    model_result = modelled.get_result(name)
    model_df = model_result['data']
    fig2 = px.line(model_df, x='time', y=y)
    fig2.update_traces(line=dict(color="blue", width=3))

    fig = Figure(data=fig1.data + fig2.data)

    return fig


def make_new_case_plot(name):
    fig = make_validation_graph(name, 'new_cases')
    return fig


def make_total_case_plot(name):
    fig = make_validation_graph(name, 'tot_cases')
    return fig


total_cases_graph = dcc.Graph(id='total-cases-graph', responsive=True)
new_cases_graph = dcc.Graph(id='new-cases-graph', responsive=True)

validation_dropdown = html.Div([
        html.Label('validation'),
        dcc.Dropdown(
            id='validation-dropdown',
            options=[{"label": m, "value": m} for m in modelled.valid_names],
            value=modelled.valid_names[0]
        ),
    ]
)

text = html.Div(
    html.Div([
        validation_dropdown,
        total_cases_graph,
        new_cases_graph
    ], id='text-content'),
    id='text-container'
)

validation_page = [
    brand, footer, text
]

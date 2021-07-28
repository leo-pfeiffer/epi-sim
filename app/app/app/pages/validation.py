from abc import ABC
from typing import Dict

import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np
from plotly.graph_objects import Figure
import pandas as pd
import pickle
from urllib.request import urlopen
from urllib.error import HTTPError
import os
import logging

from ..mixins import SimulationTransformerMixin
from ..static_elements import brand, footer, read_markdown
from ..configuration import DATA_REPO_URL_RAW


class ValidationData(ABC):
    """
    Abstract class for the validation data.
    """

    # validation period
    MAX_TIME = 120

    @staticmethod
    def get_csv_from_repo(file) -> pd.DataFrame:
        """
        Download CSV file from data repo.
        :param file: name of file (including path in repo)
        :return: Data frame
        """
        return pd.read_csv(f"{DATA_REPO_URL_RAW}/{file}")

    @staticmethod
    def get_pickle_from_repo(file):
        """
        Read pickled file from data repo
        :param file: name of file (including path in repo)
        :return: Deserialized object
        """
        url = DATA_REPO_URL_RAW + '/' + file

        with urlopen(url) as f:
            obj = pickle.load(f)

        return obj

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
    """
    Manage empirical data set that contains the case counts for the US.
    """

    # repo URL of the US data set
    US_FILE = 'validation/case-data/us_covid_count_by_state.csv'

    # repo URL of the population data set
    POP_FILE = 'validation/case-data/us_population_by_state.csv'

    # repo URL of the precomputed data set
    ALL_STATES_FILE_NAME = 'validation/app-data/all_states.pkl'

    def __init__(self):
        super().__init__()

        # try getting the file from the data repo directly (a bit faster)
        try:
            self._states = self.get_pickle_from_repo(self.ALL_STATES_FILE_NAME)
            logging.info('Loaded states data from repo')

        # if it doesn't exist, put it together manually
        except HTTPError:
            self._covid_us = self.get_covid_us_data()
            self._pop_map = self.make_state_population()
            self._first_wave_map = self.make_first_wave_map()
            self._states = self.make_all_states()

    @property
    def states(self) -> pd.DataFrame:
        return self._states

    def get_covid_us_data(self) -> pd.DataFrame:
        """
        Extract and clean the raw covid data for the US.
        :return: clean covid data for US
        """
        raw = self.get_csv_from_repo(self.US_FILE)
        clean = self.transform_covid(raw)
        return clean

    @staticmethod
    def transform_covid(df) -> pd.DataFrame:
        """
        Transform the raw data set rad from the repo.
        :param df: Raw data frame
        :return:
        """
        # transform dates
        df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")
        df = df.sort_values('date').reset_index(drop=True)

        # convert data types
        num_cols = ['tot_cases', 'new_cases']

        col_transform = {c: 'float32' for c in num_cols if c in df.columns}

        # string formatting
        for c in col_transform:
            df[c] = df[c].apply(lambda x: x.replace(',', '') if type(x) == str else x, 1)

        df.replace('NaN', np.NaN, inplace=True)

        # transform numbers
        df = df.astype(col_transform)

        return df

    @classmethod
    def make_state_population(cls) -> Dict:
        """
        Create a dictionary containing the population for each state of the US.
        Data is read from a csv file from the data repo
        :return dictionary:
        """

        logging.info('Calculating state population')

        # read raw data
        df = cls.get_csv_from_repo(cls.POP_FILE)

        # clean data
        df['population'] = df['population'].apply(
            lambda x: x.replace(',', '') if type(x) == str else x, 1)

        df = df.astype({'population': 'float32'})

        # create correct dictionary format
        records = df.drop('state_name', 1).dropna().to_dict('records')

        return {x['state']: x['population'] for x in records}

    def make_first_wave_map(self, threshold=0.001) -> Dict:
        """
        Get first date when tot_cases / population > `threshold` for each state.
        :param threshold: Threshold for start of epidemic.
        :return dictionary:
        """

        logging.info('Compiling first wave map')

        first_wave_map = {}

        for state in self._covid_us.state.unique():
            subset = self._covid_us[self._covid_us.state == state].sort_values('date')

            if state not in self._pop_map:
                continue

            threshold_cases = self._pop_map[state] * threshold
            date = subset[subset.tot_cases >= threshold_cases].iloc[0].date
            first_wave_map[state] = date.strftime("%Y-%m-%d")

        return first_wave_map

    @staticmethod
    def extract_region(df, region_filter: Dict) -> pd.DataFrame:
        """
        Extract a single region from the full CDC data frame.
        :param df: Full data frame
        :param region_filter: dictionary containing the `column` in which to
            filter for the `value`
        :return: Data frame of region
        """
        region_col = region_filter['column']
        region_val = region_filter['value']
        df_out = df[df[region_col] == region_val].copy()
        df_out.reset_index(drop=True, inplace=True)
        return df_out

    def make_state_covid(self, state: str) -> pd.DataFrame:
        """
        Make the validation data frame for a single `state`.
        :param state: Target state
        :return: Data frame
        """

        # get the start of the epidemic
        start_date = self._first_wave_map[state]

        # filter the full data set for the current state
        state_filter = {'column': 'state', 'value': state}
        df_state = self.extract_region(self._covid_us, state_filter)

        # Keep only the data within the validation period
        df_state = self.get_data_after_date(df_state, start_date)

        # make case counts relative to population
        pop = self._pop_map[state]
        df_state = self.make_counts_relative(df_state, pop)

        return df_state

    def make_all_states(self) -> pd.DataFrame:
        """
        Make the empirical data set for all states by concatenating
        the data sets for each state.
        :return: data frame
        """

        logging.info('Compiling state validation data')

        dfs = []

        for state in self._pop_map:
            dfs.append(self.make_state_covid(state))

        return pd.concat(dfs)


class ModelledData(ValidationData, SimulationTransformerMixin):
    """
    Manage data set containing the simulation results for validation.
    """

    # Available validation files
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

    # repo URL of pre computed results
    RESULTS_FILE_NAME = 'validation/app-data/results.pkl'

    def __init__(self):
        super().__init__()

        self._results = []

        # get the pre-computed data from data repo (much faster)
        try:
            self._results = self.get_pickle_from_repo(self.RESULTS_FILE_NAME)
            logging.info('Loaded results data from repo')

        # alternatively, compute manually
        except HTTPError:
            self.make_validation_data()

    @property
    def results(self):
        return self._results

    def get_result(self, name):
        """
        Return the result of the simulation name with the provided name
        :param name: Name of the simulation run
        :return: Data set of simulation run
        """
        for r in self._results:
            if r['name'] == name:
                return r
        return None

    def make_validation_data(self):
        """
        Manually compile the validation data sets, that is bring them in the
        correct format for use in the application.
        :return: List with validation data sets
        """

        logging.info('Compiling model results')

        for v in self.VALIDATION_FILES:
            r = v.copy()

            # convert to wide format and clean
            r['data'] = self._get_wide(v['name'])
            self._results.append(r)

    @classmethod
    def _get_wide(cls, name):
        """
        Convert the raw simulation results into wide format after cleaning.
        :param name: Name of the file (in the repo)
        :return: Wide format simulation result
        """
        # get data frame
        file = '/validation/' + name + '.pkl'
        df = cls.get_pickle_from_repo(file)

        # keep only within simulation time frame
        df = df[df.time <= cls.MAX_TIME]

        # fill gaps in case of unevenly long experiments
        df = cls.fill_experiment_length_gap(df, delta=1)

        # calculate the mean values
        grouped = cls.df_group_mean(df)
        wide = grouped.pivot(index=['time'], columns=['compartment'], values='value')
        wide.reset_index(inplace=True)

        # calc new cases
        wide['new_cases'] = (wide['S'].diff().fillna(0) * (-1)).values.tolist()

        # calc total cases
        wide['tot_cases'] = wide['E'] + wide['I'] + wide['R']

        return wide


# instantiate the validation data
modelled = ModelledData()
empirical = EmpiricalData()


def make_validation_graph(name, y, title):
    fig1 = px.line(empirical.states, x='date', y=y, color='state')
    fig1.update_traces(opacity=0.2, showlegend=True)

    model_result = modelled.get_result(name)
    model_df = model_result['data']
    fig2 = px.line(model_df, x='time', y=y)
    fig2.update_traces(line=dict(color="blue", width=3), showlegend=True, name='Model')

    fig = Figure(data=fig2.data + fig1.data)
    fig.update_layout(
        title=title,
        xaxis_title="Days since start of epidemic",
        yaxis_title="Fraction of population",
    )

    return fig


def make_new_case_plot(name):
    fig = make_validation_graph(name, 'new_cases', 'New cases per day')
    return fig


def make_total_case_plot(name):
    fig = make_validation_graph(name, 'tot_cases', 'Total cumulative cases')
    return fig


def make_description_card(filename):
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, 'markdown', filename)
    return read_markdown(file)


total_cases = dbc.Card([
    dbc.CardBody(
        dcc.Graph(id='total-cases-graph', responsive=True)
    )
], id='total-cases')

new_cases = dbc.Card([
    dbc.CardBody(
        dcc.Graph(id='new-cases-graph', responsive=True)
    )
], id='new-cases')

description = dbc.Card([
    dbc.CardBody(
        dcc.Markdown(make_description_card('validation.md')),
        style={'overflowY': 'auto', 'height': '100%'}
    )
], id='validation-description')

validation_control = dbc.Card([
    html.Div([
        html.Label('Validation Setting'),
        dcc.RadioItems(
            id='validation-dropdown',
            options=[
                {"label": v['title'], "value": v['name']}
                for v in modelled.VALIDATION_FILES
            ],
            value=modelled.VALIDATION_FILES[0]['name']
        ),
    ])
], body=True, id='validation-controls')

text = html.Div(
    html.Div([

    ], id='text-content'),
    id='text-container'
)

validation_page = [
    brand,
    footer,
    validation_control,
    total_cases,
    new_cases,
    description
]

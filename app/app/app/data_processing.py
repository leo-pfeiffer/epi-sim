import sys
from typing import Dict, List

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

from abc import ABC
import numpy as np
import os
import logging
from tqdm import tqdm
import pandas as pd
import pickle
from urllib.request import urlopen
from urllib.error import HTTPError

from .configuration import DATA_REPO_URL_RAW, DATA_DIR
from .simulation_files import FILES, MODEL, NETWORK, DISEASE
from .mixins import SimulationTransformerMixin


class SimulationData(SimulationTransformerMixin):
    """
    Contains simulation data and associated functionality.
    """

    DATA_REPO_URL_RAW: Final[str] = DATA_REPO_URL_RAW
    DATA_REPO_SIMULATIONS_PATH: Final[str] = 'simulations'
    DATA_REPO_APP_DATA_PATH: Final[str] = 'app-data'

    MODEL_META = {
        'SEIR': {
            'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'
        },
        'SEIR_Q': {
            'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'
        },
        'SEIVR': {
            'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'
        },
        'SEIVR_Q': {
            'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'
        },
    }

    COLUMNS = ['experiment_id', 'time', 'compartment', 'value']

    def __init__(self):

        # file info
        self._files = FILES

        # initialise filters
        self._current_state = {}

        # track if files have been loaded yet
        self._files_loaded = False

    @property
    def files(self):
        return self._files

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        assert isinstance(new_state, dict)
        assert 'disease' in new_state
        assert 'model' in new_state
        assert 'network' in new_state
        assert 'filters' in new_state
        assert isinstance(new_state['disease'], str)
        assert isinstance(new_state['model'], str)
        assert isinstance(new_state['network'], str)
        assert isinstance(new_state['filters'], dict)
        self._current_state = new_state

    @property
    def files_loaded(self):
        return self._files_loaded

    @property
    def models(self):
        return sorted(list(set([x[MODEL] for x in self._files])))

    @property
    def networks(self):
        return sorted(list(set([x[NETWORK] for x in self._files])))

    def load_files(self):
        """
        Load all files from repo.
        :return: Updated files
        """
        pbar = tqdm(self._files)
        for file in pbar:
            self.load_file(file)
            pbar.set_description_str("Loading file %s" % file['name'])

        self._files_loaded = True

    @classmethod
    def load_file(cls, file: Dict) -> Dict:
        """
        Load JSON file from data repo inplace.
        :param file: Dict containing file info, crucially the `name`
        :return: Updated dict including the `content`
        """

        file_name = file['name'] + '.pkl'

        # check if file is available on disk
        local_file = os.path.join(DATA_DIR, file_name)
        if os.path.isfile(local_file):
            with open(local_file, 'rb') as f:
                file['df'] = pickle.load(f)

            return file

        # else, get from data repo
        url = os.path.join(
            cls.DATA_REPO_URL_RAW,
            cls.DATA_REPO_APP_DATA_PATH,
            file_name
        )

        with urlopen(url) as f:
            df = pickle.load(f)
            file['df'] = df

            # ... and save to file for next time
            df.to_pickle(local_file)

        return file

    def subset_data(self, disease: str, model: str, network: str,
                    filters: Dict) -> pd.DataFrame:
        """
        Return a subset of the data for a `model`, a `network`, and potentially
        filtered by the values specified in `filters`.
        :param disease: Disease of the subset.
        :param model: Model of the subset.
        :param network: Network of the subset.
        :param filters: Dictionary containing columns as keys and filter values
            as values
        :return: The subset as a data frame.
        """

        # make sure files are loaded ...
        assert self._files_loaded

        df = pd.DataFrame()
        found = False
        for file in self._files:
            if file[DISEASE] == disease and file[MODEL] == model and \
                    file[NETWORK] == network:

                df = file['df']
                found = True
                break

        if not found:
            raise ValueError(f"Provided combination of `model={model}` and "
                             f"`network={network}` does not exist.")

        return self._apply_filters(df, filters)

    @staticmethod
    def epidemic_size_per_param(df, param):
        """
        For the variable parameter `param` calculate the epidemic size
        for each setting and for each experiment in `df`. Return the result
        as a data frame with the columns `param` and 'epidemic_size'
        :param df: Simulation df
        :param param: Target variable parameter
        :return: data frame
        """

        time_max = df.groupby(['experiment_id', param]).agg(
            time_max=pd.NamedAgg(column='time', aggfunc='max')
        ).to_dict()['time_max']

        f = df.apply(lambda x: np.isclose(
            time_max[(x['experiment_id'], x[param])],
            x['time']) and x['compartment'] in ['R', 'E'], axis=1)

        filtered = df[f]

        epidemic_size = filtered.groupby(
            ['experiment_id', param]
        ).value.sum()

        epidemic_size = epidemic_size.reset_index()
        epidemic_size.rename(columns={'value': 'epidemic_size'}, inplace=True)

        return epidemic_size[[param, 'epidemic_size']]

    @staticmethod
    def calc_perc_infected(df):
        """
        Calculate the percentage of infected individuals from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Percentage of infected individuals.
        """
        r = df[df.compartment == 'R'].iloc[0]['value']
        e = df[df.compartment == 'E'].iloc[0]['value']
        return r + e

    @staticmethod
    def calc_susceptible_remaining(df):
        """
        Calculate the percentage of infected individuals from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Percentage of susceptible individuals remaining
        """
        susceptible = df[df.compartment == 'S'].iloc[-1]['value']

        if 'V' in df.compartment.values:
            vaccinated = df[df.compartment == 'V'].iloc[-1]['value']
        else:
            vaccinated = 0

        return susceptible + vaccinated

    @staticmethod
    def calc_peak_time(df):
        """
        Calculate the time step of peak infection from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Time step of peak infection
        """
        return df.loc[df[df.compartment == 'I'].value.idxmax(), 'time']

    @staticmethod
    def calc_peak_infected(df):
        """
        Calculate the peak infection percentage from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Peak infection percentage
        """
        return df[df.compartment == 'I'].value.max()

    @classmethod
    def calc_effective_end(cls, df):
        """
        Calculate the effective end of the epidemic, i.e. when percentage of
        infected individuals is below 1% for the first time from a simulation
        data frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Time step of effective end
        """
        # first time, infected is sub 1% again
        infected = df[df.compartment == 'I']

        idx = cls.find_sub_threshold_after_peak(infected.value.tolist(), 0.01)

        if idx is None:
            return None

        return infected.time.values[idx]

    @staticmethod
    def find_sub_threshold_after_peak(ls: List, v: float):
        """
        Find the index of the value in a list that is below a threshold  for the
        first time after a value above the peak. If the condition is not met for
        any values, return 0 if the first value of the list is below the
        threshold or None if the first value is above the threshold.
        :param ls: List of values
        :param v: Threshold value
        :return: Index or None
        """
        for i in range(1, len(ls)):
            if ls[i - 1] > v >= ls[i]:
                return i

        return 0 if len(ls) > 0 and ls[0] <= v else None


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
    VAC_STATE_FILE_NAME = 'validation/app-data/vac_state.pkl'

    def __init__(self, vac_state, vac_start):
        super().__init__()

        # try getting the file from the data repo directly (a bit faster)
        try:

            self._states = self.get_pickle_from_repo(
                self.ALL_STATES_FILE_NAME
            )

            self._vac_state = self.get_pickle_from_repo(
                self.VAC_STATE_FILE_NAME
            )

            logging.info('Loaded states data from repo')

        # if it doesn't exist, put it together manually
        except HTTPError:

            self._covid_us = self.get_covid_us_data()

            pop_df = self.get_csv_from_repo(self.POP_FILE)
            self._pop_map = self.make_state_population(pop_df)

            self._first_wave_map = self.make_first_wave_map()

            self._states = self.make_all_states()

            self._vac_state = self.make_state_covid(vac_state, vac_start)

    @property
    def states(self) -> pd.DataFrame:
        return self._states

    @property
    def vac_state(self) -> pd.DataFrame:
        return self._vac_state

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
        :return: transformed data frame
        """

        # transform dates
        df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")
        df = df.sort_values('date').reset_index(drop=True)

        # convert data types
        num_cols = ['tot_cases', 'new_cases']

        col_transform = {c: 'float32' for c in num_cols if c in df.columns}

        # string formatting
        for c in col_transform:
            df[c] = df[c].apply(
                lambda x: x.replace(',', '') if type(x) == str else x, 1
            )

        df.replace('NaN', np.NaN, inplace=True)

        # transform numbers
        df = df.astype(col_transform)

        return df

    @classmethod
    def make_state_population(cls, df) -> Dict:
        """
        Create a dictionary containing the population for each state of the US.
        Data is read from a csv file from the data repo
        :param df: raw population data frame
        :return: dictionary
        """

        logging.info('Calculating state population')

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
            subset = self._covid_us[self._covid_us.state == state].\
                sort_values('date')

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

        # todo unit tests

        region_col = region_filter['column']
        region_val = region_filter['value']
        df_out = df[df[region_col] == region_val].copy()
        df_out.reset_index(drop=True, inplace=True)
        return df_out

    @classmethod
    def get_data_after_date(cls, df, date: str):

        # todo unit tests

        df = df[df['date'] >= np.datetime64(date)].copy()
        df.reset_index(drop=True, inplace=True)

        start_date = df.loc[0, 'date'].date()
        df['date'] = df['date'].apply(lambda x: (x.date() - start_date).days)

        df = df.loc[df['date'] <= cls.MAX_TIME, :].copy()

        return df

    @staticmethod
    def make_counts_relative(df, population: float) -> pd.DataFrame:
        """
        Divide case counts by population to get relative case counts
        :param df: data frame with case counts
        :param population: population
        :return: data frame
        """

        # todo unit tests

        df['new_cases'] = [
            c / population for c in df['new_cases'].values.tolist()
        ]

        df['tot_cases'] = [
            c / population for c in df['tot_cases'].values.tolist()
        ]

        return df

    def make_state_covid(self, state: str, custom_start=None) -> pd.DataFrame:
        """
        Make the validation data frame for a single `state`.
        :param state: Target state
        :param custom_start: custom start date not from first wave map
        :return: Data frame
        """

        # get the start of the epidemic
        if custom_start:
            start_date = custom_start
        else:
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
        {
            'name': 'v_seir_mobility_pre',
            'title': 'SEIR, M (Pre)',
            'model': 'SEIR'
        },
        {
            'name': 'v_seirq_25_mobility_pre',
            'title': 'SEIR_Q (p=0.25), M (Pre)',
            'model': 'SEIR_Q'
        },
        {
            'name': 'v_seirq_50_mobility_pre',
            'title': 'SEIR_Q (p=0.5), M (Pre)',
            'model': 'SEIR_Q'
        },
        {
            'name': 'v_seirq_75_mobility_pre',
            'title': 'SEIR_Q (p=0.75), M (Pre)',
            'model': 'SEIR_Q'
        },

        {
            'name': 'v_seir_mobility_post',
            'title': 'SEIR, M (Post)',
            'model': 'SEIR'
        },
        {
            'name': 'v_seirq_25_mobility_post',
            'title': 'SEIR_Q (p=0.25), M (Post)',
            'model': 'SEIR_Q'
        },
        {
            'name': 'v_seirq_50_mobility_post',
            'title': 'SEIR_Q (p=0.5), M (Post)',
            'model': 'SEIR_Q'
        },
        {
            'name': 'v_seirq_75_mobility_post',
            'title': 'SEIR_Q (p=0.75), M (Post)',
            'model': 'SEIR_Q'
        },

        {
            'name': 'v_seivr_mobility_pre',
            'title': 'SEIVR, M (Pre)',
            'model': 'SEIVR'
        },
        {
            'name': 'v_seivrq_25_mobility_pre',
            'title': 'SEIVR_Q (p=0.25), M (Pre)',
            'model': 'SEIVR_Q'
        },
        {
            'name': 'v_seivrq_50_mobility_pre',
            'title': 'SEIVR_Q (p=0.5), M (Pre)',
            'model': 'SEIVR_Q'
        },
        {
            'name': 'v_seivrq_75_mobility_pre',
            'title': 'SEIVR_Q (p=0.75), M (Pre)',
            'model': 'SEIVR_Q'
        },

        {
            'name': 'v_seivr_mobility_post',
            'title': 'SEIVR, M (Post)',
            'model': 'SEIVR'
        },
        {
            'name': 'v_seivrq_25_mobility_post',
            'title': 'SEIVR_Q (p=0.25), M (Post)',
            'model': 'SEIVR_Q'
        },
        {
            'name': 'v_seivrq_50_mobility_post',
            'title': 'SEIVR_Q (p=0.5), M (Post)',
            'model': 'SEIVR_Q'
        },
        {
            'name': 'v_seivrq_75_mobility_post',
            'title': 'SEIVR_Q (p=0.75), M (Post)',
            'model': 'SEIVR_Q'
        },
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
            r['data'] = self._get_wide(v['name'], v['model'])
            self._results.append(r)

    @classmethod
    def _get_wide(cls, name, model):
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
        wide = grouped.pivot(
            index=['time'], columns=['compartment'], values='value'
        )
        wide.reset_index(inplace=True)

        # calc new cases
        if model in ['SEIR', 'SEIR_Q']:
            new_cases = (wide['S'].diff().fillna(0) * (-1)).values.tolist()

            # back-fill first day
            if len(new_cases) > 1:
                new_cases[0] = new_cases[1]
            wide['new_cases'] = new_cases

        # calc total cases
        wide['tot_cases'] = wide['E'] + wide['I'] + wide['R']

        return wide

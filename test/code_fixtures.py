import pytest
import py
from psycopg2.extras import NumericRange
import os
from pandas import date_range

_dir = os.path.dirname(os.path.realpath(__file__))
FIXTURE_DIR = py.path.local(_dir) / '/home/581/pxp581/clef'


@pytest.fixture(scope="module")
def nranges(request):
    return [NumericRange(207501, 210013, '[)'),
                NumericRange(200601, 204013, '[)'), 
                NumericRange(204101, 207413, '[)'),]

@pytest.fixture(scope="module")
def periods(request):
    period1 = [('20750101', '21001231'), ('20060101', '20401231'), 
             ('20410101', '20741231')]
    period2 = [('20050201', '20050228'), ('20050101', '20050131')] 
    return period1, period2

@pytest.fixture(scope="module")
def dates(request):
    dates1 = [date_range('20050101', '20050228', freq='D')]
    dates2 = [date_range('20050101', '20050131', freq='D')]
    dates2.append(date_range('20050201', '20050228', freq='D'))
    dates3 = [date_range('20750101', '21001231', freq='M')]
    dates3.append(date_range('20060101', '20401231', freq='M'))
    dates3.append(date_range('20410101', '20741231', freq='M'))
    dates4 = [date_range('20750101', '21001231', freq='M')]
    dates4.append(date_range('20060101', '20401231', freq='M'))
    return dates1, dates2, dates3, dates4

@pytest.fixture(scope="module")
def empty(request):
    return []

@pytest.fixture(scope="module")
def c5_kwargs(request):
    return {'model': 'INM-CM4', 'e': 'rcp85', 'variable': 'tas', 'table': 'Amon', 'f': 'mon',
            'institute': 'MIROC', 'experiment_family': 'RCP', 'member': 'r1i1p1'}

@pytest.fixture(scope="module")
def c5_vocab(request):
    return ([ 'INM-CM4'], ['atmos'], ['tas'], ['mon'],
           [ 'Amon'], ['rcp85'], ['RCP'])

@pytest.fixture(scope="module")
def c5_keys(request):
    return {'model': ['source_id', 'model', 'm'], 'realm': ['realm'], 'time_frequency': ['time_frequency', 'frequency', 'f'], 'variable': ['variable_id', 'variable', 'v'], 'experiment': ['experiment_id', 'experiment', 'e'], 'cmor_table': ['table_id', 'table', 'cmor_table', 't'], 'ensemble': ['member_id', 'member', 'ensemble', 'en', 'mi'], 'institute': ['institution_id', 'institution', 'institute'], 'experiment_family': ['experiment_family']}


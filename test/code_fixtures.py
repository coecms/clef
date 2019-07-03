import pytest
import py
from psycopg2.extras import NumericRange
import os
from pandas import date_range
from clef.code import *

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



@pytest.fixture(scope="module")
def local_results():
    """
    A successful local query returning something that is in the DB
    """
    results =  [
# mod1 has both pr and tas for r1 but not for r2 version is always v1 
# mod1 is in rr3
    {'filenames': ['tas.nc'], 'project': 'CMIP5', 'institute': 'I1', 'model': 'mod1', 'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos', 'r': '1', 'i': '1', 'p': '1', 'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas', 'pdir': '/g/data1/rr3/publications/CMIP5/output1/I1/mod1/exp1/mon/atmos/Amon/r1i1p1/latest/tas', 'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231', 'time_complete': True}
    {'filenames': ['pr.nc'], 'project': 'CMIP5', 'institute': 'I1', 'model': 'mod1', 'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos', 'r': '1', 'i': '1', 'p': '1', 'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr', 'pdir': '/g/data1/rr3/publications/CMIP5/output1/I1/mod1/exp1/mon/atmos/Amon/r1i1p1/latest/pr', 'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231', 'time_complete': True}
    {'filenames': ['pr.nc'], 'project': 'CMIP5', 'institute': 'I1', 'model': 'mod1', 'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos', 'r': '2', 'i': '1', 'p': '1', 'ensemble': 'r2i1p1', 'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr', 'pdir': '/g/data1/rr3/publications/CMIP5/output1/I1/mod1/exp1/mon/atmos/Amon/r2i1p1/latest/pr', 'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231', 'time_complete': True}
# mod2 has both pr and tas for r1 and for exp1 and exp2 but tas is v1 and pr is v2 
    {'filenames': ['pr.nc'], 'project': 'CMIP5', 'institute': 'I2', 'model': 'mod2',
     'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos', 'r': '1', 'i': '1', 'p': '1',
      'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
      'pdir': '/g/data1/al33/replicas/CMIP5/output1/I2/mod2/exp1/mon/atmos/Amon/r1i1p1/v2/pr',
     'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231',
     'time_complete': True},
   {'filenames': ['tas.nc'], 'project': 'CMIP5', 'institute': 'I2', 
    'model': 'mod2', 'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos',
    'r': '1', 'i': '1', 'p': '1', 'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 
    'version': 'v1', 'variable': 'tas', 
    'pdir': '/g/data1/al33/replicas/CMIP5/output1/I2/mod2/exp1/mon/atmos/Amon/r1i1p1/v1/tas', 
    'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231',
    'time_complete': True},
    {'filenames': ['tas.nc'], 'project': 'CMIP5', 'institute': 'I2', 'model': 'mod2',
     'experiment': 'exp2', 'frequency': 'mon', 'realm': 'atmos', 'r': '1', 'i': '1', 'p': '1',
     'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/g/data1/al33/replicas/CMIP5/output1/I2/mod2/exp2/mon/atmos/Amon/r1i1p1/v1/tas',
     'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231',
     'time_complete': True},
    {'filenames': ['pr.nc'], 'project': 'CMIP5', 'institute': 'I2', 'model': 'mod2',
     'experiment': 'exp2', 'frequency': 'mon', 'realm': 'atmos', 'r': '2', 'i': '1', 'p': '1',
     'ensemble': 'r2i1p1', 'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
     'pdir': '/g/data1/al33/replicas/CMIP5/output1/I2/mod2/exp2/mon/atmos/Amon/r2i1p1/v2/pr',
     'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231',
     'time_complete': True},
# mod3 has both pr and tas but for different ensembles, same version
    {'filenames': ['tas.nc'], 'project': 'CMIP5', 'institute': 'I3', 'model': 'mod3',
     'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos', 'r': '1', 'i': '1', 'p': '1',
     'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/g/data1/al33/replicas/CMIP5/output1/I2/mod2/exp1/mon/atmos/Amon/r1i1p1/v1/tas',
     'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231',
     'time_complete': True},
    {'filenames': ['pr.nc'], 'project': 'CMIP5', 'institute': 'I3', 'model': 'mod3',i
     'experiment': 'exp1', 'frequency': 'mon', 'realm': 'atmos', 'r': '2', 'i': '1', 'p': '1',
     'ensemble': 'r1i1p1', 'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/g/data1/al33/replicas/CMIP5/output1/I2/mod2/exp1/mon/atmos/Amon/r1i1p1/v1/tas',
     'periods': [('18500101', '20051231')], 'fdate': '18500101', 'tdate': '20051231',
     'time_complete': True},
            ]
     return results

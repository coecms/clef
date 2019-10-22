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
           [ 'Amon'], ['rcp85'], ['variable'], ['RCP'])

@pytest.fixture(scope="module")
def c5_keys(request):
    return {'model': ['source_id', 'model', 'm'], 'realm': ['realm'], 'time_frequency': ['time_frequency', 'frequency', 'f'], 'variable': ['variable_id', 'variable', 'v'], 'experiment': ['experiment_id', 'experiment', 'e'], 'cmor_table': ['table_id', 'table', 'cmor_table', 't'], 'ensemble': ['member_id', 'member', 'ensemble', 'en', 'mi'], 'institute': ['institution_id', 'institution', 'institute'], 'experiment_family': ['experiment_family']}



@pytest.fixture(scope="module")
def local_results():
    """
    A successful local CMIP5 MAS query returning a list of dictionaries  
    """
    results =  [
# mod1 has both pr and tas for r1 but not for r2 version is always v1 
# I'm putting here only the fields that are relevant to the matching function
    {'filenames': ['tas.nc'], 'model': 'mod1', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod1/exp1/r1i1p1/tas', 'project':'CMIP5'},
    {'filenames': ['pr.nc'], 'model': 'mod1', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'pdir': '/rootdir/mod1/exp1/r1i1p1/pr', 'project':'CMIP5'},
    {'filenames': ['pr.nc'], 'model': 'mod1', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r2i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'pdir': '/rootdir/mod1/exp1/r2i1p1/pr', 'project':'CMIP5'},
# mod2 has both pr and tas for r1 and for exp1 and exp2 but tas is v1 and pr is v2 
    {'filenames': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp1',
      'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
      'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
      'pdir': '/rootdir/mod2/exp1/mon/atmos/Amon/r1i1p1/v2/pr'},
   {'filenames': ['tas.nc'],'model': 'mod2', 'experiment': 'exp1',
    'frequency': 'mon', 'ensemble': 'r1i1p1',  'project':'CMIP5',
    'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas', 
    'pdir': '/rootdir/mod2/exp1/r1i1p1/v1/tas'}, 
    {'filenames': ['tas.nc'], 'model': 'mod2','experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod2/exp2/r1i1p1/v1/tas'},
    {'filenames': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
     'pdir': '/rootdir/mod2/exp2/r1i1p1/v2/pr'},
# mod3 has both pr and tas but for different ensembles, same version
    {'filenames': ['tas.nc'], 'model': 'mod3', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod3/exp1/r1i1p1/v1/tas'},
    {'filenames': ['pr.nc'], 'model': 'mod3', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r2i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod3/exp1/r2i1p1/v1/tas'}
            ]
    return results

@pytest.fixture(scope="module")
def remote_results():
    """
    A successful remote CMIP6 ESGF query reorganised as a list of dictionaries  
    """
    results =  [
# mod1 has both pr and tas for r1 but not for r2 version is always v1 
# I'm putting here only the fields that are relevant to the matching function
    {'filenames': ['tas.nc'], 'source_id': 'mod1', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod1.exp1.Amon.r1i1p1f1.tas.v1'},
    {'filenames': ['pr.nc'], 'source_id': 'mod1', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'pr',
     'dataset_id': 'mod1.exp1.Amon.r1i1p1f1.pr.v1'},
    {'filenames': ['pr.nc'], 'source_id': 'mod1', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r2i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'pr',
     'dataset_id': 'mod1.exp1.Amon.r2i1p1f1.pr.v1'},
# mod2 has both pr and tas for r1 and for exp1 and exp2 but tas is v1 and pr is v2 
    {'filenames': ['pr.nc'], 'source_id': 'mod2', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v2', 'variable_id': 'pr',
     'dataset_id': 'mod2.exp1.Amon.r1i1p1f1.pr.v2'},
    {'filenames': ['tas.nc'], 'source_id': 'mod2', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod2.exp1.Amon.r1i1p1f1.tas.v1'},
    {'filenames': ['tas.nc'], 'source_id': 'mod2', 'experiment_id': 'exp2',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod2.exp2.Amon.r1i1p1f1.tas.v1'},
    {'filenames': ['pr.nc'], 'source_id': 'mod2', 'experiment_id': 'exp2',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v2', 'variable_id': 'pr',
     'dataset_id': 'mod2.exp2.Amon.r1i1p1f1.pr.v2'},
# mod3 has both pr and tas but for different ensembles, same version
    {'filenames': ['tas.nc'], 'source_id': 'mod3', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod3.exp1.Amon.r1i1p1f1.tas,v1'},
    {'filenames': ['pr.nc'], 'source_id': 'mod3', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'pr',
     'dataset_id': 'mod3.exp1.Amon.r1i1p1f1.pr.v1'},
            ]
    return results

@pytest.fixture(scope="module")
def mversions():
    """
    Local query results with multiple versions for same simulation, to test local_latest
    """
# mod2 has v1 and v2 for exp1, and v2 for exp2
# mod1 has v1 for exp2
    outres = [{'filenames': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp1',
      'frequency': 'mon', 'ensemble': 'r1i1p1',
      'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
      'pdir': '/rootdir/mod2/exp1/mon/atmos/Amon/r1i1p1/v2/pr'},
    {'filenames': ['pr.nc'], 'model': 'mod1','experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'pdir': '/rootdir/mod1/exp2/r1i1p1/v1/pr'},
    {'filenames': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
     'pdir': '/rootdir/mod2/exp2/r1i1p1/v2/pr'}]
    inres = outres + [
     {'filenames': ['pr.nc'],'model': 'mod2', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr', 
     'pdir': '/rootdir/mod2/exp1/r1i1p1/v1/pr'}] 
    return inres, outres

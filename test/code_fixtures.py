#!/usr/bin/env python
# Copyright 2019 ARC Centre of Excellence for Climate Extremes
# author: Paola Petrelli <paola.petrelli@utas.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import py
from psycopg2.extras import NumericRange
import os
import pandas

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
    kwa1 = {'model': 'INM-CM4', 'e': 'rcp85', 'variable': 'tas', 'table': 'Amon', 'f': 'mon',
            'institute': 'MIROC', 'experiment_family': 'RCP', 'member': 'r1i1p1'}
    kwa2 = {'model': 'INM-CM4', 'experiment': 'rcp85', 'variable': 'tas', 'cmor_table': 'Amon', 'time_frequency': 'mon',
            'institute': 'MIROC', 'experiment_family': 'RCP', 'ensemble': 'r1i1p1'}
    return kwa1, kwa2

@pytest.fixture(scope="module")
def c5_vocab(request):
    return {'model': [ 'INM-CM4'], 'realm': ['atmos'], 'variable': ['tas'], 'time_frequency': ['mon'],
           'cmor_table': [ 'Amon'], 'experiment': ['rcp85'], 'attributes': ['variable'], 'experiment_family': ['RCP']}

@pytest.fixture(scope="module")
def c5_keys(request):
    return {'model': ['source_id', 'model', 'm'], 'realm': ['realm'], 'time_frequency': ['time_frequency', 'frequency', 'f'],
            'variable': ['variable_id', 'variable', 'v'], 'experiment': ['experiment_id', 'experiment', 'e'],
            'cmor_table': ['table_id', 'table', 'cmor_table', 't'], 'ensemble': ['member_id', 'member', 'ensemble', 'en', 'mi'],
            'institute': ['institution_id', 'institution', 'institute'], 'experiment_family': ['experiment_family']}


@pytest.fixture(scope="module")
def local_results():
    """
    A successful local CMIP5 local query returning a pandas DataFrame
    """
    results =  [
# mod1 has both pr and tas for r1 but not for r2 version is always v1
# I'm putting here only the fields that are relevant to the matching function
    {'filename': ['tas.nc'], 'model': 'mod1', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod1/exp1/r1i1p1/tas', 'project':'CMIP5'},
    {'filename': ['pr.nc'], 'model': 'mod1', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'pdir': '/rootdir/mod1/exp1/r1i1p1/pr', 'project':'CMIP5'},
    {'filename': ['pr.nc'], 'model': 'mod1', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r2i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'pdir': '/rootdir/mod1/exp1/r2i1p1/pr', 'project':'CMIP5'},
# mod2 has both pr and tas for r1 and for exp1 and exp2 but tas is v1 and pr is v2
    {'filename': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp1',
      'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
      'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
      'pdir': '/rootdir/mod2/exp1/mon/atmos/Amon/r1i1p1/v2/pr'},
   {'filename': ['tas.nc'],'model': 'mod2', 'experiment': 'exp1',
    'frequency': 'mon', 'ensemble': 'r1i1p1',  'project':'CMIP5',
    'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
    'pdir': '/rootdir/mod2/exp1/r1i1p1/v1/tas'},
    {'filename': ['tas.nc'], 'model': 'mod2','experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod2/exp2/r1i1p1/v1/tas'},
    {'filename': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
     'pdir': '/rootdir/mod2/exp2/r1i1p1/v2/pr'},
# mod3 has both pr and tas but for different ensembles, same version
    {'filename': ['tas.nc'], 'model': 'mod3', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod3/exp1/r1i1p1/v1/tas'},
    {'filename': ['pr.nc'], 'model': 'mod3', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r2i1p1', 'project':'CMIP5',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'tas',
     'pdir': '/rootdir/mod3/exp1/r2i1p1/v1/tas'}
            ]
    return pandas.DataFrame(results)

@pytest.fixture(scope="module")
def remote_results():
    """
    A successful remote CMIP6 ESGF query reorganised as a pandas DataFrame
    """
    results =  [
# mod1 has both pr and tas for r1 but not for r2 version is always v1
# I'm putting here only the fields that are relevant to the matching function
    {'filename': ['tas.nc'], 'source_id': 'mod1', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod1.exp1.Amon.r1i1p1f1.tas.v1'},
    {'filename': ['pr.nc'], 'source_id': 'mod1', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'pr',
     'dataset_id': 'mod1.exp1.Amon.r1i1p1f1.pr.v1'},
    {'filename': ['pr.nc'], 'source_id': 'mod1', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r2i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'pr',
     'dataset_id': 'mod1.exp1.Amon.r2i1p1f1.pr.v1'},
# mod2 has both pr and tas for r1 and for exp1 and exp2 but tas is v1 and pr is v2
    {'filename': ['pr.nc'], 'source_id': 'mod2', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v2', 'variable_id': 'pr',
     'dataset_id': 'mod2.exp1.Amon.r1i1p1f1.pr.v2'},
    {'filename': ['tas.nc'], 'source_id': 'mod2', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod2.exp1.Amon.r1i1p1f1.tas.v1'},
    {'filename': ['tas.nc'], 'source_id': 'mod2', 'experiment_id': 'exp2',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod2.exp2.Amon.r1i1p1f1.tas.v1'},
    {'filename': ['pr.nc'], 'source_id': 'mod2', 'experiment_id': 'exp2',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v2', 'variable_id': 'pr',
     'dataset_id': 'mod2.exp2.Amon.r1i1p1f1.pr.v2'},
# mod3 has both pr and tas but for different ensembles, same version
    {'filename': ['tas.nc'], 'source_id': 'mod3', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'tas',
     'dataset_id': 'mod3.exp1.Amon.r1i1p1f1.tas,v1'},
    {'filename': ['pr.nc'], 'source_id': 'mod3', 'experiment_id': 'exp1',
     'frequency': 'mon', 'member_id': 'r1i1p1if1',
     'table_id': 'Amon', 'version': 'v1', 'variable_id': 'pr',
     'dataset_id': 'mod3.exp1.Amon.r1i1p1f1.pr.v1'},
            ]
    return pandas.DataFrame(results)

@pytest.fixture(scope="module")
def mversions():
    """
    Local query results with multiple versions for same simulation, to test local_latest
    """
# mod2 has v1 and v2 for exp1, and v2 for exp2
# mod1 has v1 for exp2
    outres = [{'filename': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp1',
      'frequency': 'mon', 'ensemble': 'r1i1p1',
      'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
      'path': '/rootdir/mod2/exp1/mon/atmos/Amon/r1i1p1/v2/pr'},
    {'filename': ['pr.nc'], 'model': 'mod1','experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'path': '/rootdir/mod1/exp2/r1i1p1/v1/pr'},
    {'filename': ['pr.nc'], 'model': 'mod2', 'experiment': 'exp2',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v2', 'variable': 'pr',
     'path': '/rootdir/mod2/exp2/r1i1p1/v2/pr'}]
    inres = outres + [
     {'filename': ['pr.nc'],'model': 'mod2', 'experiment': 'exp1',
     'frequency': 'mon', 'ensemble': 'r1i1p1',
     'cmor_table': 'Amon', 'version': 'v1', 'variable': 'pr',
     'path': '/rootdir/mod2/exp1/r1i1p1/v1/pr'}]
    return pandas.DataFrame(inres), pandas.DataFrame(outres)

@pytest.fixture(scope="module")
def dids6():
    '''List of CMIP6 dataset_ids
    '''
    return ['CMIP6.CMIP.NCC.NorESM2-LM.historical.r3i1p1f1.day.tas.gn.v20190920',
            'CMIP6.CMIP.NUIST.NESM3.historical.r2i1p1f1.day.tas.gn.v20190812']

@pytest.fixture(scope="module")
def results6():
    '''Corresponding list of results for dids6
    '''
    return pandas.DataFrame([{'project': 'CMIP6', 'activity_id': 'CMIP', 'institution_id': 'NCC',
              'source_id': 'NorESM2-LM', 'experiment_id': 'historical',
              'member_id': 'r3i1p1f1', 'table_id': 'day',
              'variable_id': 'tas', 'grid_label': 'gn', 'version': 'v20190920'},
            {'project': 'CMIP6', 'activity_id': 'CMIP', 'institution_id': 'NUIST',
              'source_id': 'NESM3', 'experiment_id': 'historical',
              'member_id': 'r2i1p1f1', 'table_id': 'day',
              'variable_id': 'tas', 'grid_label': 'gn', 'version': 'v20190812'}])


@pytest.fixture(scope="module")
def dids5():
    '''List of CMIP5 dataset_ids
    '''
    return ['cmip5.output1.ICHEC.EC-EARTH.historical.day.atmos.day.r5i1p1.v1',
            'cmip5.output.MIROC.MIROC5.historical.day.atmos.day.r2i1p1.v20120101']

@pytest.fixture(scope="module")
def results5():
    '''Corresponding list of results for dids5
    '''
    return pandas.DataFrame([{'project': 'cmip5', 'product': 'output1', 'institute': 'ICHEC',
              'model': 'EC-EARTH', 'experiment': 'historical', 'time_frequency': 'day',
              'realm': 'atmos', 'cmor_table': 'day', 'ensemble': 'r5i1p1',
              'version': 'v1'},
            {'project': 'cmip5', 'product': 'output', 'institute': 'MIROC',
              'model': 'MIROC5', 'experiment': 'historical', 'time_frequency': 'day',
              'realm': 'atmos', 'cmor_table': 'day', 'ensemble': 'r2i1p1',
              'version': 'v20120101'}])

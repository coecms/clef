#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Extremes
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

from clef.code import and_filter, matching, local_latest, search, stats, ids_df
from code_fixtures import *
from clef.exception import ClefException

# Tests for the functions defined in code.py


def test_and_filter(local_results, remote_results):
    # test local CMIP5 query results applying AND to variables and model, ensemble and experiment to identify run
    kwargs = {'experiment': ['exp1','exp2'], 'variable': ['tas','pr'],
              'cmor_table': ['Amon'], 'ensemble': ['r1i1p1','r2i1p1']}
    # first selection should return mod1/exp1/r1i1p1
    # mod2/exp1/r1i1p1
    # mod2/exp2/r1i1p1
    rows, selection = and_filter(local_results, ['variable'],['model','ensemble','experiment'], **kwargs)
    assert selection['comb'][0] == { ('tas', ), ('pr', )}
    assert len(selection.index) == 3
    assert len(rows.index) == 6 
    # test local CMIP5 query results applying AND to variables, experiments and model, ensemble to identify run
    rows, selection = and_filter(local_results, ['variable','experiment'],
                ['model','ensemble'], **kwargs)
    assert selection['comb'][0] == { ('tas', 'exp1'), ('pr', 'exp1'),
                                     ('tas', 'exp2'), ('pr', 'exp2')}
    assert len(selection.index) == 1 
    assert len(rows.index) == 4

    # test no match returned, used same example as above but remove from results all models apart from mod1 first
    limited = local_results[local_results['model'] == 'mod1']
    rows, selection = and_filter(limited, ['variable','experiment'],
                ['model','ensemble'], **kwargs)
    assert len(selection.index) == 0 
    assert len(rows.index) == 0 

    # test remote CMIP6 query results apply AND to variables and model, member, experiment to identify run
    kwargs = {'experiment_id': ['exp1','exp2'], 'variable_id': ['tas','pr'],
              'table_id': ['Amon'], 'member_id': ['r1i1p1f1','r2i1p1f1']}
    rows, selection = and_filter(remote_results, ['variable_id'],
                ['source_id','member_id','experiment_id'], **kwargs)
    assert selection['comb'][0] == { ('tas', ), ('pr', )}
    assert len(selection.index) == 4 
    assert len(rows.index) == 8
    dids = rows['dataset_id'].tolist()
    assert 'mod1.exp1.Amon.r2i1p1f1.pr.v1' not in dids
    assert 'mod1.exp1.Amon.r1i1p1f1.pr.v1' in dids

    # test remote CMIP6 query results apply AND to variables, experiments and model, member to identify run
    rows, selection = and_filter(remote_results, ['variable_id','experiment_id'],
                           ['source_id','member_id'], **kwargs)
    assert selection['comb'][0] == { ('tas', 'exp1'), ('pr', 'exp1'),
                                     ('tas', 'exp2'), ('pr', 'exp2')}
    assert len(selection.index) == 1 
    assert len(rows.index) == 4

    # test remote CMIP6 query results apply AND to variables and model, member, experiment and version to identify run
    results, selection = and_filter(remote_results, ['variable_id'],
                ['source_id','member_id','experiment_id','version'], **kwargs)
    assert 'mod2' not in rows['source_id']
    assert len(selection.index) == 2 
    assert len(rows.index) == 4


def test_local_latest(mversions):
    noresult = pandas.DataFrame({})
    oneresult = pandas.DataFrame({'A': 'a', 'B': 'b'}, index=[0])
    assert local_latest(noresult).empty
    assert local_latest(oneresult).equals(oneresult)
    out = local_latest(mversions[0])
    assert len(out.index) == len(mversions[1].index)
    assert out[ out['path'] == '/rootdir/mod2/exp1/r1i1p1/v1/pr' ].empty 
    assert len(local_latest(mversions[1]).index) == len(mversions[1].index)


@pytest.mark.production
def test_search(session):
    with pytest.raises(ClefException):
        search(session, project='cmip5', model='bad')
    with pytest.raises(ClefException):
        search(session, project='CMIP5', foo='blarg')

    facets = {
        'experiment':'historical',
        'cmor_table':'Amon',
        'ensemble':'r1i1p1',
        'variable':'tas'
    }

    r0 = search(session, project='cmip5', model='ACCESS1.0', **facets)
    # missing assertion

def test_stats(local_results, results5, results6):
    sdf =  stats(local_results)
    assert sorted(sdf.loc['mod1', 'members']) == ['r1i1p1','r2i1p1']
    assert sdf['count'].sum() == 5
    assert sorted(sdf.index.values) == ['mod1', 'mod2', 'mod3']
    sdf =  stats(results6)
    assert sorted(sdf.loc['NorESM2-LM','members']) == ['r3i1p1f1']
    assert sdf['count'].sum() == 2
    assert sorted(sdf.index.unique()) == ['NESM3', 'NorESM2-LM']
    sdf =  stats(results5)
    assert sorted(sdf.loc['EC-EARTH','members']) == ['r5i1p1']
    assert sdf['count'].sum() == 2
    assert sorted(sdf.index.unique()) == ['EC-EARTH', 'MIROC5']


@pytest.mark.production
def test_search_results(session):
    facets = {
        'experiment':'historical',
        'cmor_table':'Amon',
        'ensemble':'r1i1p1',
        'variable':'tas'
    }

    r0 = search(session, project='cmip5', model='ACCESS1.0', **facets)
    assert len(r0) == 1, "Only one result"
    assert r0.iloc[0]['model'] == 'ACCESS1.0', "Model matches input"

    r1 = search(session, project='cmip5', model='ACCESS1-0', **facets)
    assert len(r1) == len(r0), "Same result with filtered name"
    assert r1.iloc[0]['model'] == 'ACCESS1.0', "Model is cleaned"

    # No variable constraint
    facets.pop('variable')
    r2 = search(session, project='cmip5', model='ACCESS1-0', **facets)
    assert len(r2) == 48

    r3 = search(session, project='cmip6', model='AWI-CM-1-1-MR',
                experiment='historical', variable='uas', cmor_table='3hr')
    assert r3.iloc[0]['path'] == '/g/data/oi10/replicas/CMIP6/CMIP/AWI/AWI-CM-1-1-MR/historical/r1i1p1f1/3hr/uas/gn/v20181218'

def test_matching(session):
    facets = {
        'experiment':['historical'],
        'cmor_table':'Amon',
        'ensemble':'r1i1p1',
        'variable': ['x'],
    }
    # Errors should print a message and return 'None'
    r = matching(session, ['variable','experiment'],['model','ensemble'], **facets)
    assert r is None


def test_ids_df(dids6, results6, dids5, results5):
    assert ids_df(dids6).equals(results6)
    assert ids_df(dids5).equals(results5)

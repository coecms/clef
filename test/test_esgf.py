#!/usr/bin/env python
# Copyright 2017 ARC Centre of Excellence for Climate Systems Science
# author: Scott Wales <scott.wales@unimelb.edu.au>
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
from __future__ import print_function

from clef.esgf import *

try:
    import unittest.mock as mock
except ImportError:
    import mock

import pytest

def empty_query(*args, **kwags):
    """
    A query with no matches
    """
    response =  {
            'response': {
                'numFound': 0,
                }
            }
    return response

def missing_query(*args, **kwags):
    """
    A query returning something not in the local DB
    """
    response =  {
            'responseHeader': {'params': {'rows': 1}},
            'response': {
                'numFound': 1,
                'docs': [{
                    'id': 'abcde',
                    'checksum': ['1234'],
                    'title': 'foo',
                    'version': '1',
                    'score': 1.0,
                    'dataset_id': 'dataset_bar|example.com',
                    }],
                }
            }
    return response

def present_query(*args, **kwags):
    """
    A query returning something that is in the DB
    """
    response =  {
            'responseHeader': {'params': {'rows': 1}},
            'response': {
                'numFound': 1,
                'docs': [{
                    'id': 'abcde',
                    'checksum': ['6cf73c8c375f0005fa6dea53608a660e'],
                    'title': 'clt_3hr_ACCESS1-3_1pctCO2_r1i1p1_036001010130-036412312230.nc',
                    'version': '1',
                    'latest': 'true',
                    'score': 1.0,
                    'dataset_id': 'dataset_bar|example.com',
                    }],
                }
            }
    return response

def partial_query(*args, **kwargs):
    """
    A query returning a dataset we have only some files of
    """
    response =  {
            'responseHeader': {'params': {'rows': 2}},
            'response': {
                'numFound': 2,
                'docs': [{
                    'id': 'abcde',
                    'checksum': ['6cf73c8c375f0005fa6dea53608a660e'],
                    'title': 'clt_3hr_ACCESS1-3_1pctCO2_r1i1p1_036001010130-036412312230.nc',
                    'version': '1',
                    'latest': 'true',
                    'score': 1.0,
                    'dataset_id': 'dataset_bar|example.com',
                    }, {
                    'id': 'abcde',
                    'checksum': ['1234'],
                    'title': 'foo',
                    'version': '1',
                    'score': 1.0,
                    'dataset_id': 'dataset_bar|example.com',
                    }],
                }
            }
    return response

def updated_query(*args, **kwags):
    """
    A query returning something that is in the DB, but has been updated on ESGF
    """
    response =  {
            'responseHeader': {'params': {'rows': 1}},
            'response': {
                'numFound': 1,
                'docs': [{
                    'id': 'abcde',
                    'checksum': ['1234'],
                    'version': '2',
                    'title': 'clt_3hr_ACCESS1-3_1pctCO2_r1i1p1_036001010130-036412312230.nc',
                    'latest': 'true',
                    'score': 1.0,
                    'dataset_id': 'dataset_bar|example.com',
                    }],
                }
            }
    return response

def test_checksum_id_empty(session):
    """
    Raise an exception if not matches found on ESGF
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=empty_query):
        with pytest.raises(Exception):
            table = find_checksum_id('')

def test_checksum_id_missing(session):
    """
    Create a values table with the returned result
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=missing_query):
        table = find_checksum_id('')
        match = session.query(table).one()
        assert match.id == 'abcde'
        assert match.score == 1.0
        assert match.checksum == '1234'

def test_find_local_path_missing(session):
    """
    No local results found, return nothing
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=missing_query):
        subq = match_query(session, '')
        results = find_local_path(session, subq)
        assert results.count() == 0

def test_find_local_path_present(session):
    """
    One local result found, return its path
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=present_query):
        subq = match_query(session, '')
        results = find_local_path(session, subq)
        assert results.count() == 1

def test_find_missing_id_missing(session):
    """
    No local results found, return the missing match
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=missing_query):
        subq = match_query(session, '')
        results = find_missing_id(session, subq)
        assert results.count() == 1

def test_find_missing_id_present(session):
    """
    One local result found, return nothing
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=present_query):
        subq = match_query(session, '')
        results = find_missing_id(session, subq)
        assert results.count() == 0

def test_find_missing_id_updated(session):
    """
    File has been updated, but is still present
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=updated_query):
        subq = match_query(session, '')
        results = find_missing_id(session, subq)
        assert results.count() == 0

def test_find_local_path_updated(session):
    """
    File has been updated, but is still present
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=updated_query):
        subq = match_query(session, '')
        results = find_local_path(session, subq)
        assert results.count() == 1

def test_find_missing_id_updated_latest(session):
    """
    File has been updated, but is still present
    latest=true should prefer ESGF replies when they have the latest flag
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=updated_query):
        subq = match_query(session, '')
        results = find_missing_id(session, subq, latest=True)
        assert results.count() == 1

def test_find_local_path_updated_latest(session):
    """
    File has been updated, but is still present
    latest=true should prefer ESGF replies when they have the latest flag
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=updated_query):
        subq = match_query(session, '')
        results = find_local_path(session, subq, latest=True)
        assert results.count() == 0

def test_find_missing_id_dataset(session):
    with mock.patch('clef.esgf.esgf_query', side_effect=missing_query):
        subq = match_query(session, '')
        results = find_missing_id(session, subq, oformat='dataset')
        assert results.count() == 1
        assert results[0][0] == 'dataset_bar'

def test_find_local_path_dataset(session):
    with mock.patch('clef.esgf.esgf_query', side_effect=present_query):
        subq = match_query(session, '')
        results = find_local_path(session, subq, oformat='dataset')
        assert results.count() == 1
        assert results[0][0] == '/g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-3/1pctCO2/3hr/atmos/3hr/r1i1p1/v20121011/clt/'

def test_find_partial_dataset(session):
    """
    Dataset is only partially available
    Return no match by default
    """
    with mock.patch('clef.esgf.esgf_query', side_effect=missing_query):
        subq = match_query(session, '')
        results = find_local_path(session, subq, oformat='dataset')
        assert results.count() == 0


def test_find_cmip6():
    r = esgf_query(query='', fields='id', project='CMIP6', limit=0)
    assert r['response']['numFound'] > 0

def test_find_cmip5():
    r = esgf_query(query='', fields='id', project='CMIP5', limit=0)
    assert r['response']['numFound'] > 0

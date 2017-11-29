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

from arccssive2.esgf import *

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
                    'tracking_id': ['abcd'],
                    'version': '1',
                    'score': 1.0,
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
                    'checksum': ['3ea60eacd2a6e98b13fc3b242f585fdc'],
                    'tracking_id': ['fd1c7ee4-e150-4270-b248-77e7a26e23bb'],
                    'version': '1',
                    'score': 1.0,
                    }],
                }
            }
    return response

def updated_query(*args, **kwags):
    """
    A query returning something that is in the DB, but has a new version
    """
    response =  {
            'responseHeader': {'params': {'rows': 1}},
            'response': {
                'numFound': 1,
                'docs': [{
                    'id': 'abcde',
                    'checksum': ['1234'],
                    'tracking_id': ['fd1c7ee4-e150-4270-b248-77e7a26e23bb'],
                    'version': '2',
                    'score': 1.0,
                    }],
                }
            }
    return response

def test_checksum_id_empty(session):
    """
    Raise an exception if not matches found on ESGF
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=empty_query):
        with pytest.raises(Exception):
            table = find_checksum_id('')

def test_checksum_id_missing(session):
    """
    Create a values table with the returned result
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=missing_query):
        table = find_checksum_id('')
        match = session.query(table).one()
        assert match.id == 'abcde'
        assert match.score == 1.0
        assert match.checksum == '1234'

def test_find_local_path_missing(session):
    """
    No local results found, return nothing
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=missing_query):
        results = find_local_path(session, '')
        assert results.count() == 0

def test_find_local_path_present(session):
    """
    One local result found, return its path
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=present_query):
        results = find_local_path(session, '')
        assert results.count() == 1

def test_find_missing_id_missing(session):
    """
    No local results found, return the missing match
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=missing_query):
        results = find_missing_id(session, '')
        assert results.count() == 1

def test_find_missing_id_present(session):
    """
    One local result found, return nothing
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=present_query):
        results = find_missing_id(session, '')
        assert results.count() == 0

def test_find_local_path_updated(session):
    """
    One local result found, but it has been updated. return the local file
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=updated_query):
        results = find_local_path(session, '')
        assert results.count() == 1

def test_find_missing_id_updated(session):
    """
    One local result found, but it has been updaded. return nothing
    """
    with mock.patch('arccssive2.esgf.esgf_query', side_effect=updated_query):
        results = find_missing_id(session, '')
        assert results.count() == 0

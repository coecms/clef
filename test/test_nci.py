#!/usr/bin/env python
"""
file:   test/test_nci.py
author: Scott Wales <scott.wales@unimelb.edu.au>

Copyright 2018 ARC Centre of Excellence for Climate Systems Science

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pytest
import os
import clef.api
import clef.model as model
import clef.esgf as esgf
from sqlalchemy.orm import aliased

if os.environ.get('TRAVIS', None) is not None:
    pytest.skip("Skipping NCI-only tests on Travis", allow_module_level=True)


@pytest.fixture(scope='session')
def mas_session():
    clef.db.connect(debug=True)
    session = clef.db.Session()
    yield session
    session.rollback()


def test_search_access_latest(mas_session):
    query = {
        'variable': 'tasmin',
        'experiment': 'historical', 
        'cmor_table': 'Amon',
        'model': 'ACCESS1.0',
        'latest': True,
    }

    r = clef.api.esgf_query(session=mas_session, **query)

    esgf_response = esgf.esgf_query(query='', fields='id', **query)

    # No missing files for ACCESS models
    assert r.filter('id' == None).count() == 0
    assert r.filter('path' == None).count() == 0
    assert r.count() == esgf_response['response']['numFound']

    assert r.first().id is not None
    assert r.first().dataset_id is not None
    assert r.first().Path is not None


def test_search_access_all(mas_session):
    query = {
        'variable': 'tasmin',
        'experiment': 'historical', 
        'cmor_table': 'Amon',
        'model': 'ACCESS1.0',
        'ensemble': 'r1i1p1',
    }

    r = clef.api.esgf_query(session=mas_session, **query)

    esgf_response = esgf.esgf_query(query='', fields='id', **query)

    # No missing files for ACCESS models - but some files may have multiple matches
    assert r.filter('id' == None).count() == 0
    assert r.filter('path' == None).count() == 0


def test_search_access_join(mas_session):
    query = {
        'variable': 'tasmin',
        'experiment': 'historical', 
        'cmor_table': 'Amon',
        'model': 'ACCESS1.0',
        'ensemble': 'r1i1p1',
        'latest': True
    }

    r1 = clef.api.esgf_query(session=mas_session, **query)

    assert r1.count() > 0

    r2 = (clef.api.esgf_query(session=mas_session, **query)
            .with_entities('id', model.Path, model.C5Dataset)
            .join(model.Path.c5dataset))

    assert r1.count() == r2.count()

    assert r2.first().id is not None
    assert r2.first().Path is not None
    assert r2.first().C5Dataset is not None

    for m in r2:
        print(m.id, m.Path.path, m.C5Dataset.model)

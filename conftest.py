#!/usr/bin/env python
from __future__ import print_function
import pytest
import clef.db
import os

# Add test fixtures here so they are accessible from doctests
@pytest.fixture(scope='session')
def session():
    clef.db.connect(url = 
            os.environ.get('CLEF_DB', 
                'postgresql://postgres:@localhost/postgres'), debug=True)
    session = clef.db.Session()
    yield session
    session.rollback()

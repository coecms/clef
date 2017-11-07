#!/usr/bin/env python
from __future__ import print_function
import pytest
import arccssive2.db
import os

# Add test fixtures here so they are accessible from doctests
@pytest.fixture(scope='session')
def session():
    arccssive2.db.connect(url = 
            os.environ.get('ARCCSSIVE_DB', 
                'postgresql://postgres:@localhost/postgres'))
    session = arccssive2.db.Session()
    yield session
    session.rollback()

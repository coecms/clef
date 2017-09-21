#!/usr/bin/env python
from __future__ import print_function
import pytest
import arccssive2.db

# Add test fixtures here so they are accessible from doctests
@pytest.fixture(scope='session')
def session():
    arccssive2.db.connect(user='saw562')
    session = arccssive2.db.Session()
    yield session
    session.rollback()

#!/usr/bin/env python
from __future__ import print_function
import pytest
import clef.db
import os
import sqlalchemy as sa
from urllib.parse import urlparse

def pytest_addoption(parser):
    parser.addoption('--db', help='Database URL', default='postgresql://postgres:@localhost/postgres')

def pytest_configure(config):
    config.addinivalue_line(
            "markers", "production: mark test to require the production database"
            )

def pytest_runtest_setup(item):
    for mark in item.iter_markers(name='production'):
        db = item.config.getoption('db')
        url = urlparse(db)
        if url.hostname != 'clef.nci.org.au':
            pytest.skip('Not the production db')


# Add test fixtures here so they are accessible from doctests
@pytest.fixture(scope='session')
def session(pytestconfig):
    url = pytestconfig.getoption('db')
    engine = sa.create_engine(url)
    Session = sa.orm.sessionmaker(bind=engine)

    # Ensure read-only
    @sa.event.listens_for(Session, 'before_flush')
    def recv_before_flush(*args,**kwargs):
        raise Exception("Read only session!")

    session = Session()
    yield session
    session.rollback()

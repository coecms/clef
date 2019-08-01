#!/usr/bin/env python
from __future__ import print_function
import pytest
import clef.db
import os
import sqlalchemy as sa

def pytest_addoption(parser):
    parser.addoption('--db', help='Database URL', default='postgresql://postgres:@localhost/postgres')


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

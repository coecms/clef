import pytest
import py
import os

_dir = os.path.dirname(os.path.realpath(__file__))
FIXTURE_DIR = py.path.local(_dir) / '/home/581/pxp581/clef'


@pytest.fixture(scope="module")
def qm():
    """
    A query returning something not in the local DB
    """
    qm = [('dataset1.output.b',),
          ('dataset1.output.b',),
          ('dataset2',),
          ('dataset2',),
          ('dataset3',)]
    return qm

@pytest.fixture(scope="module")
def rows6():
    """
    The dictionary representation of the CMIP6_queue_table.csv
    """
    rows6 =  {'dataset3': 'done',
              'dataset5': 'done', 'dataset4': 'queued',
              'dataset6': 'done', 'dataset2': 'queued',
              'dataset7': 'done', 'dataset8': 'queued'}
    return rows6

@pytest.fixture(scope="module")
def rows5():
    """
    The dictionary representation of the CMIP5_queue_table.csv
    """
    rows5 =  {('dataset1.output1.b','tas'): 'done', ('dataset1.output1.b','pr'): 'done',
              ('dataset5','wmo'): 'done', ('dataset3', 'wmo'): 'queued',
              ('dataset6','pr'): 'done', ('dataset2','pr'): 'queued',
              ('dataset7','tas'): 'done', ('dataset8','tas'): 'queued'}
    return rows5

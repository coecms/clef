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

from arccssive2.cli import *
import pytest
from arccssive2.db import connect

from click.testing import CliRunner
from test_esgf import updated_query

try:
    import unittest.mock as mock
except ImportError:
    import mock

@pytest.fixture(scope='module')
def runner():
    return CliRunner()

def test_local(runner):
    result = runner.invoke(local, ['--help'])
    assert result.exit_code == 0

def dummy_connect(*args, **kwargs):
    return None

@pytest.fixture()
def mock_query(session):
    with mock.patch('arccssive2.cli.connect', side_effect=dummy_connect):
        with mock.patch('arccssive2.cli.Session', side_effect = lambda: session):
            with mock.patch('arccssive2.esgf.esgf_query', side_effect=updated_query) as query:
                yield query

@pytest.mark.parametrize('command', [local, missing])
def test_versions(command, runner, mock_query):
    """
    Check the --latest/--all-versions flags are passed correctly to esgf_query
    """

    # Check the query args are passed correctly
    result = runner.invoke(command)
    print(result.output)
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] == None

    result = runner.invoke(command, ['--all-versions'])
    print(result.output)
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] == None

    result = runner.invoke(command, ['--latest'])
    print(result.output)
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] == 'true'

@pytest.mark.parametrize('command', [local, missing])
def test_mip(command, runner, mock_query):
    result = runner.invoke(command, ['--mip=Amon'])
    print(result.output)
    assert mock_query.called
    assert mock_query.call_args[1]['cmor_table'] == ['Amon']

    result = runner.invoke(command, ['--mip=Amon', '-t', 'day'])
    print(result.output)
    assert mock_query.called
    assert mock_query.call_args[1]['cmor_table'] == ['Amon', 'day']


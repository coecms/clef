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

from clef.cli import *
import pytest

from click.testing import CliRunner
from test_esgf import updated_query

try:
    import unittest.mock as mock
except ImportError:
    import mock

@pytest.fixture(scope='module')
def runner():
    return CliRunner()

@pytest.mark.parametrize('command', [cmip5, cmip6])
def test_cmip(command, runner):
    result = runner.invoke(command, ['--help'])
    assert result.exit_code == 0

def dummy_connect(*args, **kwargs):
    return None

@pytest.fixture()
def mock_query(session):
    with mock.patch('clef.cli.connect', side_effect=dummy_connect):
        with mock.patch('clef.cli.Session', side_effect = lambda: session):
            with mock.patch('clef.esgf.esgf_query', side_effect=updated_query) as query:
                yield query

def cli_run(runner, cmd, args=[]):
    ctx = {'search':False, 'local': False, 'missing': False, 'request': False}
    result = runner.invoke(cmd, args, obj=ctx, catch_exceptions=False)
    assert result.exit_code == 0
    return result

@pytest.mark.parametrize('command', [cmip5, cmip6])
def test_versions(command, runner, mock_query):
    """
    Check the --latest/--all-versions flags are passed correctly to esgf_query
    """

    # Check the query args are passed correctly
    cli_run(runner, command)
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] == None

    cli_run(runner, command, ['--all-versions'])
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] == None

    cli_run(runner, command, ['--latest'])
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] == 'true'

@pytest.mark.parametrize('command', [cmip5])
def test_mip(command, runner, mock_query):
    cli_run(runner, command, ['--mip=Amon'])
    assert mock_query.called
    assert mock_query.call_args[1]['cmor_table'] == ['Amon']

    cli_run(runner, command, ['--mip=Amon', '-t', 'day'])
    assert mock_query.called
    assert mock_query.call_args[1]['cmor_table'] == ['Amon', 'day']


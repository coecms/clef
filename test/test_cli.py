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
import sys
import logging

try:
    import unittest.mock as mock
except ImportError:
    import mock

@pytest.fixture(scope='module')
def runner():
    return CliRunner()

@pytest.mark.parametrize('command', [clef, cmip5, cmip6])
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
    ctx = {'search':False, 'local': False, 'missing': False, 'request': False, 'flow': 'default',
            'log': logging.getLogger('cleflog')}
    result = runner.invoke(cmd, args, obj=ctx, catch_exceptions=False)
    print(result.output, file=sys.stderr)
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
    assert mock_query.call_args[1]['latest'] is True

    cli_run(runner, command, ['--all-versions'])
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] is None

    cli_run(runner, command, ['--latest'])
    assert mock_query.called
    assert mock_query.call_args[1]['latest'] is True


@pytest.mark.parametrize('command', [cmip5])
def test_mip(command, runner, mock_query):
    cli_run(runner, command, ['--mip=3hr'])
    assert mock_query.called
    assert mock_query.call_args[1]['cmor_table'] == ('3hr',)


@pytest.mark.parametrize('command', [cmip5, cmip6])
def test_remote(command, runner, mock_query):
    ctx = {'search':False, 'local': False, 'missing': False, 'request': False, 'flow': 'remote',
            'log': logging.getLogger('cleflog')}
    result = runner.invoke(command, [], obj=ctx, catch_exceptions=False)
    assert result.exit_code == 0
    assert mock_query.called


def test_variable(runner, mock_query):
    cli_run(runner, cmip5, ['--variable=ts', '--variable=ua'])
    assert mock_query.called
    assert set(mock_query.call_args[1]['variable']) == set(['ts', 'ua'])

    cli_run(runner, cmip6, ['--variable=ts', '--variable=ua'])
    assert mock_query.called
    assert set(mock_query.call_args[1]['variable_id']) == set(['ts', 'ua'])


def test_model(runner, mock_query):
    cli_run(runner, cmip5, ['--model=ACCESS1.3'])
    assert mock_query.called
    assert mock_query.call_args[1]['model'] == ['ACCESS1.3']

    cli_run(runner, cmip5, ['--model=CESM1-BGC'])
    assert mock_query.called
    assert mock_query.call_args[1]['model'] == ['CESM1(BGC)']

    cli_run(runner, cmip6, ['--model=CNRM-CM6-1'])
    assert mock_query.called
    assert mock_query.call_args[1]['source_id'] == ('CNRM-CM6-1',)

@pytest.fixture
def prod_cli(runner, session):
    with mock.patch('clef.cli.connect', side_effect=dummy_connect):
        with mock.patch('clef.cli.Session', side_effect = lambda: session):
            with mock.patch('clef.cli.config_log', side_effect = lambda: logging.getLogger()):
                def cli(argv):
                    return runner.invoke(clef, argv, catch_exceptions=False)

                yield cli


@pytest.mark.production
def test_cmip5_missing(prod_cli):
    facets = ['--model=MPI-ESM-P','--experiment=past1000',
        '--frequency=day', '--realm=atmos']

    r = prod_cli(['cmip5', *facets, '--variable=tas'])
    assert r.output == ("\nAvailable on ESGF but not locally:\n" +
        "cmip5.output1.MPI-M.MPI-ESM-P.past1000.day.atmos.day.r1i1p1.v20111028 tas\n")

    r = prod_cli(['cmip5', *facets])
    assert r.output == ("\nAvailable on ESGF but not locally:\n" +
        "cmip5.output1.MPI-M.MPI-ESM-P.past1000.day.atmos.day.r1i1p1.v20111028\n")

    r = prod_cli(['--local', 'cmip5', *facets])
    assert r.output == ''

    r = prod_cli(['--remote', 'cmip5', *facets])
    assert r.output == 'cmip5.output1.MPI-M.MPI-ESM-P.past1000.day.atmos.day.r1i1p1.v20111028\n'

    with mock.patch('clef.cli.write_request') as write_request:
        r = prod_cli(['--request', 'cmip5', *facets, '--variable=tas'])
        write_request.assert_called_with('CMIP5', ['cmip5.output1.MPI-M.MPI-ESM-P.past1000.day.atmos.day.r1i1p1.v20111028 tas'])

    with pytest.raises(ClefException):
        r = prod_cli(['--request', 'cmip5', *facets])

@pytest.mark.production
def test_cmip5_present(prod_cli):
    facets = ['--model=ACCESS1.0','--experiment=historical',
            '--frequency=mon', '--realm=atmos', '--variable=tas', '--ensemble=r1i1p1']

    r = prod_cli(['cmip5', *facets])
    assert r.output == ("/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/"+
                        "atmos/Amon/r1i1p1/latest/tas/\n\n" +
                        "Everything available on ESGF is also available locally\n")

    r = prod_cli(['--local', 'cmip5', *facets])
    assert r.output == ("/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/"+
                       "atmos/Amon/r1i1p1/latest/tas\n")

    r = prod_cli(['--remote', 'cmip5', *facets])
    assert r.output == "cmip5.output1.CSIRO-BOM.ACCESS1-0.historical.mon.atmos.Amon.r1i1p1.v20120727\n"

    r = prod_cli(['--request', 'cmip5', *facets])
    assert r.output == ("/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/latest/tas/\n\n" +
            "Everything available on ESGF is also available locally\n")

@pytest.mark.production
def test_cmip5_experiment_family(prod_cli):
    r = prod_cli(['--remote', 'cmip5','--model=ACCESS1.0','--experiment_family=RCP',
        '--frequency=mon','--variable=tas'])
    assert r.output == """
cmip5.output1.CSIRO-BOM.ACCESS1-0.rcp45.mon.atmos.Amon.r1i1p1.v20120727
cmip5.output1.CSIRO-BOM.ACCESS1-0.rcp85.mon.atmos.Amon.r1i1p1.v20120727
""".lstrip()

    r = prod_cli(['cmip5','--model=ACCESS1.0','--experiment_family=RCP',
        '--frequency=mon','--variable=tas'])
    assert r.output == """
/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/rcp45/mon/atmos/Amon/r1i1p1/latest/tas/
/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/rcp85/mon/atmos/Amon/r1i1p1/latest/tas/

Everything available on ESGF is also available locally
""".lstrip()

    r = prod_cli(['--local', 'cmip5','--model=ACCESS1.0', '--experiment=historical', '--experiment_family=RCP',
        '--frequency=mon','--variable=tas'])
    assert r.output == ""

    r = prod_cli(['--local', 'cmip5','--model=ACCESS1.0', '--experiment=rcp45', '--experiment_family=RCP',
        '--frequency=mon','--variable=tas'])
    assert r.output == """
/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/rcp45/mon/atmos/Amon/r1i1p1/latest/tas
""".lstrip()

    r = prod_cli(['--local', 'cmip5','--model=ACCESS1.0', '--experiment_family=RCP',
        '--frequency=mon','--variable=tas'])
    assert r.output == """
/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/rcp45/mon/atmos/Amon/r1i1p1/latest/tas
/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/rcp85/mon/atmos/Amon/r1i1p1/latest/tas
""".lstrip()

@pytest.mark.production
def test_cmip6_present(prod_cli):
    facets = ['--model=UKESM1-0-LL','--experiment=historical','--frequency=mon','--variable=tas','--variant_label=r1i1p1f2']

    r = prod_cli(['cmip6', *facets])
    assert r.output == ("/g/data/oi10/replicas/CMIP6/CMIP/MOHC/UKESM1-0-LL/historical/r1i1p1f2/Amon/tas/gn/v20190406/\n\n" +
        "Everything available on ESGF is also available locally\n")

    r = prod_cli(['--local', 'cmip6', *facets])
    assert r.output == "/g/data/oi10/replicas/CMIP6/CMIP/MOHC/UKESM1-0-LL/historical/r1i1p1f2/Amon/tas/gn/v20190406\n"

    r = prod_cli(['--remote', 'cmip6', *facets])
    assert r.output == "CMIP6.CMIP.MOHC.UKESM1-0-LL.historical.r1i1p1f2.Amon.tas.gn.v20190406\n"

    r = prod_cli(['--request', 'cmip6', *facets])
    assert r.output == ("/g/data/oi10/replicas/CMIP6/CMIP/MOHC/UKESM1-0-LL/historical/r1i1p1f2/Amon/tas/gn/v20190406/\n\n" +
                        "Everything available on ESGF is also available locally\n")

@pytest.mark.production
def test_cmip6_missing(prod_cli):
    facets = ['--model=UKESM1-0-LL','--experiment=historical','--frequency=mon','--variable=tasmin','--variant_label=r2i1p1f2']

    r = prod_cli(['cmip6', *facets])
    assert r.output == ("\nAvailable on ESGF but not locally:\n"+
        "CMIP6.CMIP.MOHC.UKESM1-0-LL.historical.r2i1p1f2.Amon.tasmin.gn.v20190708\n")

    r = prod_cli(['--local', 'cmip6', *facets])
    assert r.output == ""

    r = prod_cli(['--remote', 'cmip6', *facets])
    assert r.output == "CMIP6.CMIP.MOHC.UKESM1-0-LL.historical.r2i1p1f2.Amon.tasmin.gn.v20190708\n"

    with mock.patch('clef.cli.write_request') as write_request:
        r = prod_cli(['--request', 'cmip6', *facets])
        write_request.assert_called_with('CMIP6', ['CMIP6.CMIP.MOHC.UKESM1-0-LL.historical.r2i1p1f2.Amon.tasmin.gn.v20190708'])

@pytest.mark.production
def test_cmip6_and(prod_cli):
    facets = ['--model=UKESM1-0-LL','--experiment=historical','--frequency=mon','--variable=tasmin','--variable=tasmax','--variant_label=r1i1p1f2']
    r = prod_cli(['--local', 'cmip6', *facets, '--and=variable_id'])
    assert r.output == "UKESM1-0-LL r1i1p1f2 {'v20190627'}\n"

    r = prod_cli(['--remote', 'cmip6', *facets, '--and=variable_id'])
    assert r.output == "UKESM1-0-LL r1i1p1f2 {'v20190627'}\n"

@pytest.mark.production
def test_csv_stats(prod_cli):
    facets = ['--model=UKESM1-0-LL','--experiment=historical','--frequency=mon','--variable=tasmax','--variant_label=r1i1p1f2']
    r = prod_cli(['--local', 'cmip6', *facets, '--stats'])
    # assert stats is True
    assert 'Query summary' in r.output
    # assert csvf is False
    r = prod_cli(['--local', 'cmip6', *facets, '--csv'])
    # assert stats is False
    assert 'Query summary' not in r.output
    # assert csvf is True
    r = prod_cli(['--remote', 'cmip6', *facets, '--stats'])
    # assert stats is True
    assert 'Query summary' in r.output
    # assert csvf is False
    r = prod_cli(['--remote', 'cmip6', *facets, '--csv'])
    # assert stats is False
    assert 'Query summary' not in r.output
    # assert csvf is True

@pytest.mark.production
def test_fs38_present(prod_cli):
    facets = ['--model=ACCESS-CM2','--experiment=historical','--frequency=mon','--variable=tas','--variant_label=r1i1p1f1']

    r = prod_cli(['cmip6', *facets])
    assert r.output == ("/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Amon/tas/gn/v20191108/\n\n" +
        "Everything available on ESGF is also available locally\n")

    r = prod_cli(['--local', 'cmip6', *facets])
    assert r.output == "/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Amon/tas/gn/v20191108\n"

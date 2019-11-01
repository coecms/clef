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
from .db import connect, Session
from .model import Path, C5Dataset, C6Dataset, ExtendedMetadata, Checksum
from .esgf import match_query, find_local_path, find_missing_id, find_checksum_id
from .download import *
from . import collections as colls 
from .exception import ClefException
from .code import load_vocabularies, call_local_query, fix_model, fix_path, matching, write_csv, print_stats
import click
import logging
from datetime import datetime
from sqlalchemy import any_, or_
from sqlalchemy.orm import aliased
import sys
import six
import os
import stat
import json
import pkg_resources
import re

def clef_catch():
    debug_logger = logging.getLogger('clex_debug')
    debug_logger.setLevel(logging.CRITICAL)
    try:
        clef()
    except Exception as e:
        click.echo('ERROR: %s'%e)
        debug_logger.exception(e)
        sys.exit(1)


@click.group()
@click.option('--remote', 'flow', is_flag=True, default=False, flag_value='remote', 
               help="returns only ESGF search results")
@click.option('--local', 'flow', is_flag=True, default=False, flag_value='local', 
               help="returns only local files matching arguments in MAS database")

@click.option('--missing', 'flow', is_flag=True, default=False, flag_value='missing',
               help="returns only missing files matching ESGF search")
@click.option('--request', 'flow', is_flag=True, default=False, flag_value='request',
               help="send NCI request to download missing files matching ESGF search")
@click.option('--debug', is_flag=True, default=False,
               help="Show debug info")
@click.pass_context
def clef(ctx, flow, debug):
    ctx.obj={}
    # set up a default value for flow if none selected for logging
    if flow is None: flow = 'default'
    ctx.obj['flow'] = flow
    ctx.obj['log'] = config_log()

    if debug:
        debug_logger = logging.getLogger('clex_debug')
        debug_logger.setLevel(logging.DEBUG)
    

def config_log():
    ''' configure log file to keep track of users queries '''
    # start a logger
    logger = logging.getLogger('cleflog')
    # set a formatter to manage the output format of our handler
    formatter = logging.Formatter('%(asctime)s; %(message)s',"%Y-%m-%d %H:%M:%S")
    # set the level for the logger, has to be logging.LEVEL not a string
    # until we do so cleflog doesn't have a level and inherits the root logger level:WARNING
    logger.setLevel(logging.INFO)
    
    # add a handler to send WARNING level messages to console
    clog = logging.StreamHandler()
    clog.setLevel(logging.WARNING)
    logger.addHandler(clog)    

    # add a handler to send INFO level messages to file 
    # the messagges will be appended to the same file
    # create a new log file every month
    month = datetime.now().strftime("%Y%m") 
    logname = '/g/data/ua8/Download/CMIP6/clef_log_' + month + '.txt' 
    flog = logging.FileHandler(logname) 
    try:
        os.chmod(logname, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO);
    except OSError:
        pass 
    flog.setLevel(logging.INFO)
    flog.setFormatter(formatter)
    logger.addHandler(flog)

    # return the logger object
    return logger

def warning(message):
    print("WARNING: %s"%message, file=sys.stderr)


def cmip5_args(f):
    models, realms, variables, frequencies, tables, experiments, families, attributes = load_vocabularies('CMIP5')
    constraints = [
        click.option('--experiment', '-e', multiple=True, type=click.Choice(experiments), metavar='x',
                      help="CMIP5 experiment: piControl, rcp85, amip ..."),
        click.option('--experiment_family',multiple=False, type=click.Choice(families),
                      help="CMIP5 experiment family: Decadal, RCP ..."),
        click.option('--model', '-m', multiple=True, type=click.Choice(models),  metavar='x', 
                      help="CMIP5 model acronym: ACCESS1.3, MIROC5 ..."),
        click.option('--table', '--mip', '-t', 'cmor_table', multiple=True, type=click.Choice(tables) ),
        click.option('--variable', '-v', multiple=True, type=click.Choice(variables), metavar='x',
                      help="Variable name as shown in filanames: tas, pr, sic ... "),
        click.option('--ensemble', '--member', '-en', 'ensemble', multiple=True, help="CMIP5 ensemble member: r#i#p#"),
        click.option('--frequency', 'time_frequency', multiple=True, type=click.Choice(frequencies) ), 
        click.option('--realm', multiple=True, type=click.Choice(realms) ),
        click.option('--and', 'and_attr', multiple=True, type=click.Choice(attributes),
                      help="Attributes for which we want to add AND filter, i.e. -v tasmin -v tasmax --and variable will return only model/ensemble that have both"),
        click.option('--institution', 'institute', multiple=True, help="Modelling group institution id: MIROC, IPSL, MRI ...")
    ]
    for c in reversed(constraints):
        f = c(f)
    return f

def common_args(f):
    constraints = [
        click.argument('query', nargs=-1),
        click.option('--cf_standard_name',multiple=True, help="CF variable standard_name, use instead of variable constraint "),
        click.option('--format', 'oformat', type=click.Choice(['file','dataset']), default='dataset',
                     help="Return output for datasets (default) or individual files"),
        click.option('--latest/--all-versions', 'latest', default=True,  
                     help="Return only the latest version or all of them. Default: --latest"),
        click.option('--replica/--no-replica', default=False, 
                     help="Return both original files and replicas. Default: --no-replica"),
        click.option('--distrib/--no-distrib', 'distrib', default=True, 
                     help="Distribute search across all ESGF nodes. Default: --distrib"),
        click.option('--csv/--no-csv', 'csvf', default=False,
                     help="Send output to csv file including extra information, works only with --local option. Default: --no-csv"),
        click.option('--stats/--no-stats',  default=False,
                     help="Write summary of query results, works only with --local option. Default: --no-stats"),
        click.option('--debug/--no-debug', default=False,
                     help="Show debug output. Default: --no-debug")
    ]
    for c in reversed(constraints):
        f = c(f)
    return f

def cmip6_args(f):
# 
    models, realms, variables, frequencies, tables, experiments, activities, stypes, attributes = load_vocabularies('CMIP6')
    constraints = [
        click.option('--activity', '-mip', 'activity_id', multiple=True, type=click.Choice(activities) ) ,
        click.option('--experiment', '-e', 'experiment_id', multiple=True, type=click.Choice(experiments), metavar='x',
                     help="CMIP6 experiment, list of available depends on activity"),
        click.option('--source_type',multiple=True, type=click.Choice(stypes) ),
        click.option('--table', '-t', 'table_id', multiple=True, type=click.Choice(tables), metavar='x',
                     help="CMIP6 CMOR table: Amon, SIday, Oday ..."),
        click.option('--model', '--source_id','-m', 'source_id', multiple=True, type=click.Choice(models),  metavar='x',
                     help="CMIP6 model id: GFDL-AM4, CNRM-CM6-1 ..."),
        click.option('--variable', 'variable_id', '-v', multiple=True, type=click.Choice(variables),  metavar='x', 
                     help="CMIP6 variable name as in filenames"),
        click.option('--member', '-mi', 'member_id', multiple=True, help="CMIP6 member id: <sub-exp-id>-r#i#p#f#"),
        click.option('--grid', '--grid_label', '-g', 'grid_label', multiple=True, help="CMIP6 grid label: i.e. gn for the model native grid"),
        click.option('--resolution', '--nominal_resolution','-nr' , 'nominal_resolution', multiple=True, help="Approximate resolution: '250 km', pass in quotes"),
        click.option('--frequency',multiple=True, type=click.Choice(frequencies) ),
                     # help="Frequency"),
        click.option('--realm', multiple=True, type=click.Choice(realms) ),
                     # help="CMIP6 realm"),
        click.option('--sub_experiment_id', '-se', multiple=True, help="Only available for hindcast and forecast experiments: sYYYY"),
        click.option('--variant_label', '-vl', multiple=True, help="Indicates a model variant: r#i#p#f#"),
        click.option('--and', 'and_attr', multiple=True, type=click.Choice(attributes),
                      help="Attributes for which we want to add AND filter, i.e. -v tasmin -v tasmax --and variable_id will return only model/ensemble that have both"),
        click.option('--institution', 'institution_id', multiple=True, help="Modelling group institution id: IPSL, NOAA-GFDL ...")
    ]
    for c in reversed(constraints):
        f = c(f)
    return f


def ds_args(f):
    #st_names = dataset.standard_names()
    #cm_names = dataset.cmor_names()
    #variables = dataset.vars_names()
    st_names = ['air_temperature','air_pressure','rainfall_rate']
    cm_names = ['ps','pres','psl','tas','ta','pr','tos']
    variables = ['T','U','V','Z']
    constraints = [
        click.option('--dataset', '-d', 'dname',  multiple=False, help="Dataset name"),
        click.option('--version', '-v', multiple=False, help="Dataset version"),
        click.option('--format', '-f', 'fileformat', multiple=False, type=click.Choice(['netcdf','grib','HDF5','binary']),
                      help="Dataset file format as defined in clef.db Dataset table"),
        click.option('--standard-name', '-sn', multiple=True, type=click.Choice(st_names),
        #click.option('--standard-name', '-sn', multiple=False, type=click.Choice(st_names),
                      help="Variable standard_name this is the most reliable way to look for a variable across datasets"),
        click.option('--cmor-name', '-cn', multiple=True, type=click.Choice(cm_names),
        #click.option('--cmor-name', '-cn', multiple=False, type=click.Choice(cm_names),
                      help="Variable cmor_name useful to look for a variable across datasets"),
        click.option('--variable', '-va', 'varname', multiple=True, type=click.Choice(variables), 
                      help="Variable name as defined in files: tas, pr, sic, T ... "),
        click.option('--frequency', 'frequency', multiple=True, type=click.Choice(['yr','mon','day','6hr','3hr','1hr']), 
                      help="Time frequency on which variable is defined"),
        click.option('--from-date', 'fdate', multiple=False, help="""To define a time range of availability of a variable, 
                      can be used on its own or together with to-date. Format is YYYYMMDD"""),
        click.option('--to-date', 'tdate', multiple=False, help="""To define a time range of availability of a variable, 
                      can be used on its own or together with from-date. Format is YYYYMMDD""")
    ]
    for c in reversed(constraints):
        f = c(f)
    return f

@clef.command()
@cmip5_args
@common_args
@click.pass_context
def cmip5(ctx, query, debug, distrib, replica, latest, oformat, csvf, stats,
        cf_standard_name,
        ensemble,
        experiment,
        experiment_family,
        institute,
        cmor_table,
        model,
        realm,
        time_frequency,
        variable,
        and_attr
        ):
    """
    Search ESGF and local database for CMIP5 files

    Constraints can be specified multiple times, in which case they are combined    using OR: -v tas -v tasmin will return anything matching variable = 'tas' or variable = 'tasmin'.
    The --latest flag will check ESGF for the latest version available, this is the default behaviour
    """
    project='CMIP5'

    # check model name is ESGF-valid (i.e. ACCESS1.0 no ACCESS1-0  
    if len(model) > 0: 
        model = fix_model(project, model)
    dataset_constraints = {
        'ensemble': ensemble,
        'experiment': experiment,
        'institute': institute,
        'model': model,
        'realm': realm,
        'time_frequency': time_frequency,
        'cmor_table': cmor_table,
        'variable': variable,
        'experiment_family': experiment_family,
        }

    common_esgf_cli(ctx, project, query, cf_standard_name, oformat, latest, replica, distrib, csvf, stats, debug, dataset_constraints, and_attr)


@clef.command()
@cmip6_args
@common_args
@click.pass_context
def cmip6(ctx,query, debug, distrib, replica, latest, oformat, csvf, stats,
        cf_standard_name,
        variant_label,
        member_id,
        experiment_id,
        sub_experiment_id,
        source_type,
        institution_id,
        table_id,
        source_id,
        realm,
        frequency,
        variable_id,
        activity_id,
        grid_label,
        nominal_resolution,
        and_attr
        ):
    """
    Search ESGF and local database for CMIP6 files

    Constraints can be specified multiple times, in which case they are combined    using OR: -v tas -v tasmin will return anything matching variable = 'tas' or variable = 'tasmin'.
    The --latest flag will check ESGF for the latest version available, this is the default behaviour
    """

    project='CMIP6'

    dataset_constraints = {
        'activity_id': activity_id,
        'experiment_id': experiment_id,
        'frequency': frequency,
        'grid_label': grid_label,
        'institution_id': institution_id,
        'member_id': member_id,
        'nominal_resolution': nominal_resolution,
        'realm': realm,
        'source_id': source_id,
        'source_type': source_type,
        'sub_experiment_id': sub_experiment_id,
        'table_id': table_id,
        'variable_id': variable_id,
        'variant_label': variant_label,
        }

    common_esgf_cli(ctx, project, query, cf_standard_name, oformat, latest,
        replica, distrib, csvf, stats, debug, dataset_constraints, and_attr)


def common_esgf_cli(ctx, project, query, cf_standard_name, oformat, latest,
               replica, distrib, csvf, stats, debug, constraints, and_attr):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    clef_log = ctx.obj['log']
    user_name=os.environ.get('USER','unknown')
    user=None
    connect(user=user)
    s = Session()

    matching_fixed = {
        'CMIP5': ['model','ensemble'],
        'CMIP6': ['source_id','member_id'],
        }

    # keep track of query arguments in clef_log file
    args_str = ' '.join('{}={}'.format(k,v) for k,v in constraints.items())
    clef_log.info('  ;  '.join([user_name,project,ctx.obj['flow'],args_str]))

    terms = {}
    # Add filters
    for key, value in six.iteritems(constraints):
        if value is not None and len(value) > 0:
            terms[key] = value

    if ctx.obj['flow'] == 'remote':
        if len(and_attr) > 0:
            results, selection = matching(s, and_attr, matching_fixed[project], project=project,
                                          local=False, latest=latest, **terms)
            if csvf:
                write_csv(results)
            for row in selection:
                    print(*[row[x] for x in matching_fixed[project]], row['version'])
            return
        else:
            q = find_checksum_id(' '.join(query),
                distrib=distrib,
                replica=replica,
                latest=latest,
                cf_standard_name=cf_standard_name,
                project=project,
                **constraints,
                )

            if oformat == 'file':
                for result in s.query(q):
                    print(result.id)
            else:
                ids=sorted(set(x.dataset_id for x in s.query(q)))
                for did in ids:
                    print(did)
            return

    # if local query MAS based on attributes not checksums
    if ctx.obj['flow'] == 'local':
        if len(and_attr) > 0:
            results, selection = matching(s, and_attr, matching_fixed[project], project=project,
                                          local=True, latest=latest, **terms)
            for row in selection:
                print(*[row[x] for x in matching_fixed[project]], row['version'])
        else:
            results, paths = call_local_query(s, project, oformat, latest, **terms) 
            if not stats:
                for p in paths:
                    print(p)
        if csvf:
            write_csv(results)
        if stats:
            print_stats(results)
        return 

    # if not local, query ESGF first and then MAS based on checksums
    subq = match_query(s, query=' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=(latest if latest else None),
            cf_standard_name=cf_standard_name,
            project=project,
            **terms
            )

    # Make sure that if find_local_path does an all-version search using the
    # filename, the resulting project is still CMIP6 (and not say a PMIP file
    # with the same name)
    ql = find_local_path(s, subq, oformat=oformat)

    if not ctx.obj['flow'] == 'missing':
        if project == 'CMIP5':
            # temporary fix to return only one combined path instead of 1 or 2 output ones
            cpaths = sorted(set(map(fix_path, [p[0] for p in ql])))
            for p in cpaths:
                print(p)
        else:
            for result in ql:
                print(result[0])

    qm = find_missing_id(s, subq, oformat=oformat)
    
    # if there are missing datasets, search for dataset_id in synda queue,
    #  update list and print result 
    if qm.count() > 0:
        varlist = []
        if project == 'CMIP5' and 'variable' in terms:
            varlist = terms['variable']
        updated = search_queue_csv(qm, project, varlist)
        print('\nAvailable on ESGF but not locally:')
        for result in updated:
            print(result)
    else:
        print('\nEverything available on ESGF is also available locally')
        return

    if ctx.obj['flow'] == 'request':
        if project == 'CMIP5' and len(varlist) == 0:
            raise ClefException("Please specify at least one variable to request")
        if len(updated) >0:
            write_request(project,updated)
        else:
            print("\nAll the published data is already available locally, or has been requested, nothing to request")

@clef.command()
@ds_args
def ds(**kwargs):
    """
    Search local database for non-ESGF datasets 
    """
    # open noesgf connection
    db = colls.connect()
    clefdb = db.session
    datasets, variables, varsearch = db.command_query(**kwargs)
    for ds in datasets:
        if not varsearch:
            print(" ".join([ds.name,'v'+ds.version + ":",ds.drs]))
        for v in variables:
            if v.dataset_id == ds.id:
                print(v.varname + ": " + v.path() ) 
    return

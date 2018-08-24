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
from .esgf import find_local_path, find_missing_id, find_checksum_id
import click
import logging
from sqlalchemy import any_, or_
from sqlalchemy.orm import aliased
import sys
import six
import os

@click.group()
#@click.argument('project', nargs=1)
@click.option('--search', is_flag=True, default=False, help="returns only ESGF search results")
@click.option('--local', is_flag=True, default=False, help="returns only local files matching ESGF search")
@click.option('--missing', is_flag=True, default=False, help="returns only missing files matching ESGF search")
@click.option('--request', is_flag=True, default=False,
               help="send NCI request to download missing files matching ESGF search")
@click.pass_context
#def esgf(ctx, project, search, local, missing, request):
def esgf(ctx, search, local, missing, request):
    ctx.obj={}
    #ctx.obj['project']=project.upper()
    ctx.obj['search']=search
    ctx.obj['local']=local
    ctx.obj['missing']=missing
    ctx.obj['request']=request
    
    #if project in ['cmip5','CMIP5']:
    #   ctx.forward(ctx,c5_local)     
    #   ctx.invoke(ctx,c5_local()     

def warning(message):
    print("WARNING: %s"%message, file=sys.stderr)


def cmip5_args(f):
    constraints = [
        click.option('--ensemble', '--member', '-en', 'ensemble', multiple=True, help="Constraint"),
        click.option('--experiment', '-e', multiple=True, help="Constraint"),
        click.option('--experiment_family',multiple=True, help="Constraint"),
        click.option('--institution', 'institute', multiple=True, help="Constraint"),
        click.option('--table', '--mip', '-t', 'cmor_table', multiple=True, help="Constraint"),
        click.option('--model', '-m', multiple=True, help="Constraint"),
        click.option('--frequency', 'time_frequency', multiple=True, help="Constraint"),
        click.option('--variable', '-v', multiple=True, help="Constraint")
    ]
    for c in reversed(constraints):
        f = c(f)
    return f

def common_args(f):
    constraints = [
        click.argument('query', nargs=-1),
        click.option('--user', default=None, help='Username for database'),
        click.option('--debug/--no-debug', default=False, help="Show/hide debug log"),
        click.option('--distrib/--no-distrib', default=True, help="Distributed search"),
        click.option('--replica/--no-replica', default=False, help="Search replicas"),
        click.option('--latest', 'latest', flag_value='true',  help="Latest version only"),
        click.option('--all-versions', '-a', 'latest', flag_value='all', default=True, help="All versions"),
        click.option('--format', type=click.Choice(['file','dataset']), default='dataset', help="Return dataset/directory or individual files"),
        click.option('--cf_standard_name',multiple=True, help="Constraint"),
        click.option('--realm',multiple=True, help="Constraint"),
    ]
    for c in reversed(constraints):
        f = c(f)
    return f

def cmip6_args(f):
# 
    constraints = [
        click.option('--variant_label', '-vl', multiple=True, help="Constraint"),
        click.option('--member', '-mi', 'member_id', multiple=True, help="Constraint"),
        click.option('--activity', '-mip', 'activity_id', multiple=True, help="Constraint"),
        click.option('--experiment', '-e', 'experiment_id', multiple=True, help="Constraint"),
        click.option('--sub_experiment_id', '-se', multiple=True, help="Constraint"),
        click.option('--source_type',multiple=True, help="Constraint"),
        click.option('--institution', 'institution_id', multiple=True, help="Constraint"),
        click.option('--table', '-t', 'table_id', multiple=True, help="Constraint"),
        click.option('--model', '--source_id','-m', 'source_id', multiple=True, help="Constraint"),
        click.option('--frequency',multiple=True, help="Constraint"),
        click.option('--variable', 'variable_id', '-v', multiple=True, help="Constraint"),
        click.option('--grid', '--grid_label', '-g', 'grid_label', multiple=True, help="Constraint"),
        click.option('--resolution', '--nominal_resolution','-nr' , 'nominal_resolution', multiple=True, help="Constraint")
    ]
    for c in reversed(constraints):
        f = c(f)
    return f




@esgf.command()
@common_args
@cmip5_args
@click.pass_context
def cmip5(ctx, query, user, debug, distrib, replica, latest, format,
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
        ):
    """
    Search local database for files matching the given constraints

    Constraints can be specified multiple times, in which case they are ORed.
    `%` can be used as a wildcard, e.g. `--model access%` will match ACCESS1-0
    and ACCESS1-3

    The --latest flag will check ESGF for the latest version available
    """

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()

    project='CMIP5'

    ensemble_terms = None
    model_terms = None

    dataset_constraints = {
        'ensemble': ensemble,
        'experiment': experiment,
        'institute': institute,
        'model': model,
        'realm': realm,
        'time_frequency': time_frequency,
        'cmor_table': cmor_table,
        }

    if ctx.obj['request']:
        print('Sorry! This option is not yet implemented')
        return

    if ctx.obj['search']:
        q = find_checksum_id(' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=latest,
            cf_standard_name=cf_standard_name,
            ensemble=ensemble,
            experiment=experiment,
            experiment_family=experiment_family,
            institute=institute,
            cmor_table=cmor_table,
            model=model,
            project=project,
            realm=realm,
            time_frequency=time_frequency,
            variable=variable
            )
        for result in s.query(q):
            print(result.id)
        return

    terms = {}
    filters = []

    # Add filters
    for key, value in six.iteritems(dataset_constraints):
        if len(value) > 0:
            filters.append(getattr(C5Dataset,key).ilike(any_([x for x in value])))

            # If this key was filtered get a list of the matching values, used
            # in the ESGF query
            terms[key] = [x[0] for x in (s.query(getattr(C5Dataset,key))
                .distinct()
                .filter(getattr(C5Dataset,key).ilike(any_([x for x in value]))))]

    if len(variable) > 0:
        filters.append(ExtendedMetadata.variable.ilike(any_([x for x in variable])))

        terms['variable'] = [x[0] for x in (s.query(ExtendedMetadata.variable)
            .distinct()
            .filter(ExtendedMetadata.variable.ilike(any_([x for x in variable]))))]

    #if len(version) > 0:
    #    filters.append(ExtendedMetadata.version.ilike(any_(['%d'%x for x in version])))

    ql = find_local_path(s, query=None,
            distrib=True,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            experiment_family=experiment_family,
            format=format,
            project=project,
            **terms
            )
    if not ctx.obj['missing']:
        for result in ql:
            print(result[0])
    if ctx.obj['local']: 
        return

    qm = find_missing_id(s, ' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            experiment_family=experiment_family,
            format=format,
            project=project,
            **terms
            )
    if qm.count() > 0:
        print('Available on ESGF but not locally:')
        for result in qm:
            print(result[0])

@esgf.command()
@common_args
@cmip6_args
@click.pass_context
def cmip6(ctx,query, user, debug, distrib, replica, latest, format,
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
        nominal_resolution
        ):
    """
    Search local database for files matching the given constraints

    Constraints can be specified multiple times, in which case they are ORed.
    `%` can be used as a wildcard, e.g. `--model access%` will match ACCESS1-0
    and ACCESS1-3

    The --latest flag will check ESGF for the latest version available
    """

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()

    ensemble_terms = None
    model_terms = None

    dataset_constraints = {
        'member_id': member_id,
        'activity_id': activity_id,
        'experiment_id': experiment_id,
        'sub_experiment_id': sub_experiment_id,
        'institution_id': institution_id,
        'source_id': source_id,
        'source_type': source_type,
        'realm': realm,
        'frequency': frequency,
        'table_id': table_id,
        'grid_label': grid_label,
        'nominal_resolution': nominal_resolution
        }

    if ctx.obj['request']:
        print('Sorry! This option is not yet implemented')
        return

    if ctx.obj['search']:
        q = find_checksum_id(' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=latest,
            cf_standard_name=cf_standard_name,
            variant_label=variant_label,
            member_id=member_id,
            experiment_id=experiment_id,
            source_type=source_type,
            institution_id=institution_id,
            table_id=table_id,
            source_id=source_id,
            project='CMIP6',
            realm=realm,
            frequency=frequency,
            variable_id=variable_id,
            activity_id=activity_id,
            grid_label=grid_label,
            nominal_resolution=nominal_resolution
            )
        for result in s.query(q):
            print(result.id)
        return

    terms = {}
    filters = []

    # Add filters
    for key, value in six.iteritems(dataset_constraints):
        if len(value) > 0:
            filters.append(getattr(C6Dataset,key).ilike(any_([x for x in value])))

            # If this key was filtered get a list of the matching values, used
            # in the ESGF query
            terms[key] = [x[0] for x in (s.query(getattr(C6Dataset,key))
                .distinct()
                .filter(getattr(C6Dataset,key).ilike(any_([x for x in value]))))]

    if len(variable_id) > 0:
        filters.append(ExtendedMetadata.variable.ilike(any_([x for x in variable_id])))

        terms['variable_id'] = [x[0] for x in (s.query(ExtendedMetadata.variable)
            .distinct()
            .filter(ExtendedMetadata.variable.ilike(any_([x for x in variable_id]))))]

    ql = find_local_path(s, query=None,
            distrib=True,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            format=format,
            project='CMIP6',
            **terms
            )
    if not ctx.obj['missing']:
        for result in ql:
            print(result[0])
    if ctx.obj['local']: 
        return

    qm = find_missing_id(s, ' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            format=format,
            project='CMIP6',
            **terms
            )
    
    if qm.count() > 0:
        print('Available on ESGF but not locally:')
        for result in qm:
            print(result[0])


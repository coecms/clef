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
def esgf():
    """
    Commands for searching ESGF
    """
    pass

def warning(message):
    print("WARNING: %s"%message, file=sys.stderr)


def cmip5_args(f):
    constraints = [
        click.option('--ensemble', '-en', multiple=True, help="Constraint"),
        click.option('--experiment', '-e', multiple=True, help="Constraint"),
        click.option('--experiment_family',multiple=True, help="Constraint"),
        click.option('--institute',multiple=True, help="Constraint"),
        click.option('--cmor_table', '--mip', '-t', 'cmor_table', multiple=True, help="Constraint"),
        click.option('--model', '-m', multiple=True, help="Constraint"),
        click.option('--time_frequency',multiple=True, help="Constraint"),
        click.option('--variable', '-v', multiple=True, help="Constraint"),
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
        click.option('--member_id', '-mi', multiple=True, help="Constraint"),
        click.option('--activity_id', '-mip', multiple=True, help="Constraint"),
        click.option('--experiment_id', '-e', multiple=True, help="Constraint"),
        click.option('--sub_experiment_id', '-se', multiple=True, help="Constraint"),
        click.option('--source_type',multiple=True, help="Constraint"),
        click.option('--institution_id',multiple=True, help="Constraint"),
        click.option('--table_id', '-t', multiple=True, help="Constraint"),
        click.option('--model', '--source_id','-m', 'source_id', multiple=True, help="Constraint"),
        click.option('--frequency',multiple=True, help="Constraint"),
        click.option('--variable', 'variable_id', '-v', multiple=True, help="Constraint"),
    ]
    for c in reversed(constraints):
        f = c(f)
    return f

@esgf.command()
@common_args
@cmip5_args
def cmip5(query, user, debug, distrib, replica, latest, format,
        cf_standard_name,
        ensemble,
        experiment,
        experiment_family,
        institute,
        cmor_table,
        model,
        realm,
        time_frequency,
        variable
        ):
    """
    Search ESGF, returning matching file ids
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()
    
    project='CMIP5'

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

@esgf.command()
@common_args
@cmip6_args
def cmip6(query, user, debug, distrib, replica, latest, format,
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
        activity_id
        ):
    """
    Search ESGF, returning matching file ids
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()

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
            project=project,
            realm=realm,
            frequency=frequency,
            variable_id=variable_id,
            activity_id=activity_id
            )
    
    for result in s.query(q):
        print(result.id)

@esgf.command()
@common_args
@cmip5_args
def c5_missing(query, user, debug, distrib, replica, latest, format,
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
    Search ESGF to find files not downloaded to NCI
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()

    project=('CMIP5',)

    dataset_constraints = {
        'ensemble': ensemble,
        'experiment': experiment,
        'institute': institute,
        'model': model,
        'project': project,
        'realm': realm,
        'time_frequency': time_frequency,
        'cmor_table': cmor_table,
        }
    terms = {}

    # Add filters
    for key, value in six.iteritems(dataset_constraints):
        if len(value) > 0:
            # If this key was filtered get a list of the matching values, used
            # in the ESGF query
            terms[key] = [x[0] for x in (s.query(getattr(C5Dataset,key))
                .distinct()
                .filter(getattr(C5Dataset,key).ilike(any_([x for x in value]))))]
            if len(terms[key]) == 0:
                warning("No matches found for %s: '%s'"%(key, value))
                raise Exception

    if len(variable) > 0:
        terms['variable'] = [x[0] for x in (s.query(ExtendedMetadata.variable)
            .distinct()
            .filter(ExtendedMetadata.variable.ilike(any_([x for x in variable]))))]
        if len(terms['variable']) == 0:
            warning("No matches found for %s: '%s'"%('variable', value))
            raise Exception

    q = find_missing_id(s, ' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            experiment_family=experiment_family,
            format=format,
            **terms
            )
    
    for result in q:
        print(result[0])

@esgf.command()
@common_args
@cmip5_args
def c5_local(query, user, debug, distrib, replica, latest, format,
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
        'project': project,
        'realm': realm,
        'time_frequency': time_frequency,
        'cmor_table': cmor_table,
        }
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


    q = find_local_path(s, query=None,
            distrib=True,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            experiment_family=experiment_family,
            format=format,
            **terms
            )

    for result in q:
        print(result[0])

@esgf.command()
@common_args
@cmip6_args
def c6_missing(query, user, debug, distrib, replica, latest, format,
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
        activity_id
        ):
    """
    Search ESGF to find files not downloaded to NCI
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()

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
        }
    terms = {}

    # Add filters
    for key, value in six.iteritems(dataset_constraints):
        if len(value) > 0:
            # If this key was filtered get a list of the matching values, used
            # in the ESGF query
            terms[key] = [x[0] for x in (s.query(getattr(C6Dataset,key))
                .distinct()
                .filter(getattr(C6Dataset,key).ilike(any_([x for x in value]))))]
            if len(terms[key]) == 0:
                warning("No matches found for %s: '%s'"%(key, value))
                raise Exception

    if len(variable_id) > 0:
        terms['variable_id'] = [x[0] for x in (s.query(ExtendedMetadata.variable)
            .distinct()
            .filter(ExtendedMetadata.variable.ilike(any_([x for x in variable_id]))))]
        if len(terms['variable_id']) == 0:
            warning("No matches found for %s: '%s'"%('variable_id', value))
            raise Exception

    q = find_missing_id(s, ' '.join(query),
            distrib=distrib,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            format=format,
            project='CMIP6',
            **terms
            )
    
    for result in q:
        print(result[0])


@esgf.command()
@common_args
@cmip6_args
def c6_local(query, user, debug, distrib, replica, latest, format,
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
        activity_id
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
        }
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

    #if len(version) > 0:
    #    filters.append(ExtendedMetadata.version.ilike(any_(['%d'%x for x in version])))


    q = find_local_path(s, query=None,
            distrib=True,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            cf_standard_name=cf_standard_name,
            format=format,
            project='CMIP6',
            **terms
            )

    for result in q:
        print(result[0])


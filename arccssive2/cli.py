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
from .esgf import find_local_path, find_missing_id
import click
import logging

@click.group()
def esgf():
    """
    Commands for searching ESGF
    """
    pass

@esgf.command()
@click.argument('query', nargs=-1)
@click.option('--user')
@click.option('--debug/--no-debug', default=False)
@click.option('--distrib/--no-distrib', default=True)
@click.option('--replica/--no-replica', default=False)
@click.option('--latest', 'latest', flag_value='true', default=True)
@click.option('--all-versions', 'latest', flag_value='all', is_flag=True)
@click.option('--no-latest', 'latest', flag_value='false')
@click.option('--cf_standard_name')
@click.option('--ensemble')
@click.option('--experiment')
@click.option('--experiment_family')
@click.option('--institute')
@click.option('--cmor_table')
@click.option('--model')
@click.option('--project')
@click.option('--product')
@click.option('--realm')
@click.option('--time_frequency')
@click.option('--variable')
@click.option('--variable_long_name')
@click.option('--source_id')
def local(query, user, debug, distrib, replica, latest,
        cf_standard_name,
        ensemble,
        experiment,
        experiment_family,
        institute,
        cmor_table,
        model,
        project,
        product,
        realm,
        time_frequency,
        variable,
        variable_long_name,
        source_id,
        ):
    """
    Find local files at NCI, using ESGF's search
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    connect(user=user)
    s = Session()

    q = find_local_path(s, ' '.join(query),
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
            product=product,
            realm=realm,
            time_frequency=time_frequency,
            variable=variable,
            variable_long_name=variable_long_name,
            source_id=source_id,
            )
    
    for result in q:
        print(result.path)

@esgf.command()
@click.argument('query', nargs=-1)
@click.option('--user')
@click.option('--debug/--no-debug', default=False)
@click.option('--distrib/--no-distrib', default=True)
@click.option('--replica/--no-replica', default=False)
@click.option('--latest', 'latest', flag_value='true', default=True)
@click.option('--all-versions', 'latest', flag_value='all', is_flag=True)
@click.option('--no-latest', 'latest', flag_value='false')
@click.option('--cf_standard_name')
@click.option('--ensemble')
@click.option('--experiment')
@click.option('--experiment_family')
@click.option('--institute')
@click.option('--cmor_table')
@click.option('--model')
@click.option('--project')
@click.option('--product')
@click.option('--realm')
@click.option('--time_frequency')
@click.option('--variable')
@click.option('--variable_long_name')
@click.option('--source_id')
def missing(query, user, debug, distrib, replica, latest,
        cf_standard_name,
        ensemble,
        experiment,
        experiment_family,
        institute,
        cmor_table,
        model,
        project,
        product,
        realm,
        time_frequency,
        variable,
        variable_long_name,
        source_id,
        ):
    """
    Find files using ESGF's search that aren't at NCI
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)
    print('latest: %s'%latest)

    connect(user=user)
    s = Session()

    q = find_missing_id(s, ' '.join(query),
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
            product=product,
            realm=realm,
            time_frequency=time_frequency,
            variable=variable,
            variable_long_name=variable_long_name,
            source_id=source_id,
            )
    
    for result in q:
        print(result.id)


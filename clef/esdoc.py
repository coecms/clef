#!/usr/bin/env python
# Copyright 2019 ARC Centre of Excellence for Climate Extremes
# author: Paola Petrelli <paola.petrelli@utas.edu.au>
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
#from .db import connect, Session
#from .model import Path, C5Dataset, C6Dataset, ExtendedMetadata
#from .exception import ClefException
#from .esgf import esgf_query
import requests
from bs4 import BeautifulSoup
import pandas as pd


def esdoc_urls(dataset_ids):
    """
    :input: datasets_ids (list of str) dataset_ids returned by query
    :return: esdoc_urls (list of dict), each dictionary contains the related esdoc urls for a dataset_id,
             the keys are the urls and the values are extracts from the linked information
    """
    esdoc_urls=[]
    for did in dataset_ids:
        urls={}
        #attrs = did.split(".")
        #urls['model_url'] = get_model_doc(attrs[2],attrs[3])
        wdcc_url, urls['wdcc_url'] = get_wdcc(did)
        urls['exp_url'] = ''
        #exp_url = get_exp_doc()
        esdoc_urls.append(urls)
    return esdoc_urls

def get_wdcc(dataset_id):
    ''' Retrieve metadata documentation from WDCC site, this is less detailed than esdoc but often more readable
        :input: dataset_id (str) the simulation dataset_id
        :return: wdcc_url (str) the wdcc_url for the document
        :return: r.json() (dict) the web response as json
    '''
    wdcc_root = 'https://cera-www.dkrz.de/WDCC/ui/cerasearch/'
    settings = 'select?rows=1&wt=json'
    project=dataset_id.split(".")[0]
    if project == 'cmip5':
        entry="*".join(dataset_id.split(".")[0:4])
        wdcc_url = wdcc_root + f'solr/{settings}&q=entry_name_s:{entry}'
    elif project == 'CMIP6':
        entry=".".join(dataset_id.split(".")[0:4])
        wdcc_url = wdcc_root + f'cerarest/exportcmip6?input={entry}'
    else:
        print('No wdcc documents available for this project')
        return None, None
    r = requests.get(wdcc_url)
    return wdcc_url, r.json()


def print_model(tables):
    ''' Print out esdoc CIM2 model document
        :input: tables (str) html tables downloaded from web interface
    '''
    dfs = pd.read_html(str(tables[0]))
    df = dfs[0]
    for i in range(0, df.shape[0]):
        print(df.iloc[i,0] +' > ' + df.iloc[i,1])
    for table in tables[1:]:
        dfs = pd.read_html(str(table))
        df = dfs[0]
        print(f'{df.iloc[0,0].replace(">","-")} > {df.iloc[2,1]}')
    return

def print_doc(tables, dtype):
    ''' Print out esdoc document, all types except model
        :input: tables (str?) html tables downloaded from web interface
        :input: dtype (str) - the kind of document (i.e. experiment, mip)
    '''
    for table in tables:
        dfs = pd.read_html(str(table))
        df = dfs[0]
        for i in range(0, df.shape[0]):
           if df.iloc[i,0] != 'Keywords' and df.iloc[i,1] != '--':
               print(df.iloc[i,0] +' > ' + df.iloc[i,1])
    return

def get_doc(project, dtype, name):
    ''' Retrieve esdoc document and then call function to print it to screen
        :input: project (str) - ESGF project
        :input: dtype (str) - the kind of document (i.e. experiment, mip)
        :input: name (str) - the canonical name of the related document, usually model/experiment/mip name works
    '''
    stype = {'model': 'CIM.2.SCIENCE.MODEL', 'mip': 'cim.2.designing.Project',
             'experiment': 'cim.2.designing.NumericalExperiment'}
    service = ('https://api.es-doc.org/2/document/search-name?client=ESDOC-VIEWER-DEMO&encoding=html'+
              f'&project={project}&name={name}&type={stype[dtype]}')
    r = requests.get(service)
    soup = BeautifulSoup(r.text,'lxml')
    tables = soup.findAll("table")
    if dtype == 'model':
        print_model(tables)
    else:
        print_doc(tables, dtype)
    return service

def errata(tracking_id):
    ''' return errata uids connected to a tracking id '''
    service = 'https://errata.es-doc.org/1/resolve/pid?pids='
    r = requests.get(service + tracking_id.split(":")[1])
    uids = r.json()['errata'][0][1][0][0]
    if uids:
        return [x for x in uids.split(';')]
    else:
        return None

def retrieve_error(uid):
    ''' Accept error uid and return errata as json plus webpage to view error '''
    view = 'https://errata.es-doc.org/static/view.html?uid='
    service = 'https://errata.es-doc.org/1/issue/retrieve?uid='
    r = requests.get(service + uid)
    error = {view+uid: r.json()['issue']}
    return error

def print_error(uid):
    error = retrieve_error(uid)
    for k in error.keys():
        print(f'You can view the full report online:\n{k}')
        print(f'Title: {error[k]["title"]}')
        print(f'Status: {error[k]["status"]}')
        print(f'Description: {error[k]["description"]}')


url, data = get_wdcc('CMIP5.output1.MIROC.MIROC5.historical.r1i1p1')
print(data)

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

from clef.esdoc import *
from esdoc_fixtures import *
#import pytest

def test_esdoc_urls():
    #dids=[]
    assert True

def test_get_model_doc():
    assert True

def test_get_doc():
    base = 'https://api.es-doc.org/2/document/search-name?client=ESDOC-VIEWER-DEMO&encoding=html&'
    assert get_doc('CMIP6', 'model', 'MIROC6') == ( base +
                   'project=CMIP6&name=MIROC6&type=CIM.2.SCIENCE.MODEL')
    assert get_doc('CMIP6', 'experiment', 'historical') == ( base +
                   'project=CMIP6&name=historical&type=cim.2.designing.NumericalExperiment')
    assert get_doc('CMIP6', 'mip', 'FAFMIP') == ( base +
                   'project=CMIP6&name=FAFMIP&type=cim.2.designing.Project')

def test_get_wdcc():
    did='CMIP6.CMIP.MRI.MRI-ESM2-0.historical.none.r1i1p1f1'
    url, json6 = get_wdcc(did)
    assert url == 'https://cera-www.dkrz.de/WDCC/ui/cerasearch/cerarest/exportcmip6?input=CMIP6.CMIP.MRI.MRI-ESM2-0'
    assert json6['identifier']['id'] == '10.22033/ESGF/CMIP6.621'
    did='cmip5.output1.MIROC.MIROC5.historical.mon.atmos.Amon.r1i1p1.v20111028'
    url, json5 = get_wdcc(did)
    assert url == ("https://cera-www.dkrz.de/WDCC/ui/cerasearch/solr/select?" +
                   "rows=1&wt=json&q=entry_name_s:cmip5*output1*MIROC*MIROC5")
    assert json5['response']['docs'][0]['entry_name_s'] == "cmip5 output1 MIROC MIROC5"
    did='cordex.something.or.other'
    assert get_wdcc(did) == (None, None)


def test_errata():
    assert ( errata('hdl:21.14100/e4193a02-6405-49b6-8ad3-65def741a4dd') ==
           ["b6302400-3620-c8f1-999b-d192c0349084","2f6b5963-f87e-b2df-a5b0-2f12b6b68d32"])
    assert errata('hdl:21.14100/7d16d79b-77c8-446c-9039-36c6803752f2') is None

def test_retrieve_error(test_error):
    assert retrieve_error('ce889690-1ef3-6f46-9152-ccb27fc42490') ==  test_error



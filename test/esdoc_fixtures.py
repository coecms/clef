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

import pytest

@pytest.fixture(scope="module")
def test_error():
      return {'https://errata.es-doc.org/static/view.html?uid=ce889690-1ef3-6f46-9152-ccb27fc42490':
           {'status': 'resolved', 'urls': [], 'datasets':
           ['CMIP6.AerChemMIP.NCAR.CESM2-WACCM.hist-1950HC.r1i1p1f1.AERmon.lossch4.gn#20190606',
            'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.hist-piNTCF.r1i2p1f1.AERmon.lossch4.gn#20190531',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.histSST-1950HC.r1i1p1f1.AERmon.lossch4.gn#20190531',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.histSST-piNTCF.r1i2p1f1.AERmon.lossch4.gn#20190531',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.histSST.r1i2p1f1.AERmon.lossch4.gn#20190531',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.piClim-NTCF.r1i2p1f1.AERmon.lossch4.gn#20191001',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.ssp370-lowNTCF.r1i2p1f1.AERmon.lossch4.gn#20191001',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.ssp370SST-lowNTCF.r1i1p1f1.AERmon.lossch4.gn#20191004',
'CMIP6.AerChemMIP.NCAR.CESM2-WACCM.ssp370SST.r1i1p1f1.AERmon.lossch4.gn#20191001',
'CMIP6.AerChemMIP.NCAR.CESM2.ssp370-lowNTCF.r2i2p1f1.AERmon.lossch4.gn#20191001',
'CMIP6.AerChemMIP.NCAR.CESM2.ssp370-lowNTCF.r3i2p1f1.AERmon.lossch4.gn#20191001',
'CMIP6.CMIP.NCAR.CESM2-WACCM.amip.r1i1p1f1.AERmon.lossch4.gn#20190401',
'CMIP6.CMIP.NCAR.CESM2-WACCM.amip.r2i1p1f1.AERmon.lossch4.gn#20190319',
'CMIP6.CMIP.NCAR.CESM2-WACCM.amip.r3i1p1f1.AERmon.lossch4.gn#20190319',
'CMIP6.CMIP.NCAR.CESM2-WACCM.historical.r1i1p1f1.AERmon.lossch4.gn#20190415',
'CMIP6.CMIP.NCAR.CESM2-WACCM.historical.r2i1p1f1.AERmon.lossch4.gn#20190415',
'CMIP6.CMIP.NCAR.CESM2-WACCM.historical.r3i1p1f1.AERmon.lossch4.gn#20190415',
'CMIP6.CMIP.NCAR.CESM2-WACCM.piControl.r1i1p1f1.AERmon.lossch4.gn#20190320',
'CMIP6.ScenarioMIP.NCAR.CESM2-WACCM.ssp370.r1i1p1f1.AERmon.lossch4.gn#20190815',
'CMIP6.ScenarioMIP.NCAR.CESM2-WACCM.ssp370.r2i1p1f1.AERmon.lossch4.gn#20190815',
'CMIP6.ScenarioMIP.NCAR.CESM2-WACCM.ssp370.r3i1p1f1.AERmon.lossch4.gn#20190815'],
 'description': 'lossch4 is missing a 1.e6/6.022e23 scaling factor. It can be applied manually and the data will then be correct. lossch4 will be recalculated and the data replaced.',
 'closedDate': None, 'title': 'Missing scaling factor from all lossch4 data.', 'institute': 'ncar', 'facets':
  ['esdoc:errata:project:cmip6', 'esdoc:errata:severity:critical', 'esdoc:errata:status:resolved',
  'wcrp:cmip6:activity-id:aerchemmip', 'wcrp:cmip6:activity-id:cmip', 'wcrp:cmip6:activity-id:scenariomip',
 'wcrp:cmip6:experiment-id:amip', 'wcrp:cmip6:experiment-id:hist-1950hc', 'wcrp:cmip6:experiment-id:hist-pintcf',
 'wcrp:cmip6:experiment-id:historical', 'wcrp:cmip6:experiment-id:histsst', 'wcrp:cmip6:experiment-id:histsst-1950hc',
 'wcrp:cmip6:experiment-id:histsst-pintcf', 'wcrp:cmip6:experiment-id:piclim-ntcf', 'wcrp:cmip6:experiment-id:picontrol',
 'wcrp:cmip6:experiment-id:ssp370', 'wcrp:cmip6:experiment-id:ssp370-lowntcf', 'wcrp:cmip6:experiment-id:ssp370sst',
 'wcrp:cmip6:experiment-id:ssp370sst-lowntcf', 'wcrp:cmip6:grid-label:gn', 'wcrp:cmip6:institution-id:ncar',
 'wcrp:cmip6:source-id:cesm2', 'wcrp:cmip6:source-id:cesm2-waccm', 'wcrp:cmip6:table-id:aermon'],
 'createdDate': '2019-10-11 20:19:37.255166', 'closedBy': None, 'project': 'cmip6',
 'updatedDate': '2019-10-17 16:18:09.159330', 'materials': [], 'createdBy': 'phillips-ad', 'updatedBy': 'phillips-ad',
 'uid': 'ce889690-1ef3-6f46-9152-ccb27fc42490', 'severity': 'critical'} }

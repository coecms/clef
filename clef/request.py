#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Extremes
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
from __future__ import print_function
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from bs4 import BeautifulSoup
import requests


def write_request(project,qm):
    ''' write missing dataset_ids to file to create download request for synda '''
    rootdir = '/g/data/ua8/Download/CMIP6/'
    user = os.environ['USER']
    tstamp = datetime.now().strftime("%Y%m%dT%H%M%S") 
    fname = "_".join([project,user,tstamp])+".txt" 
    f = open(rootdir+fname, 'w')
    for q in qm:
        f.write('instance_id='+q[0]+'\n')
    f.close()
    helpdesk(user, rootdir, fname, project)
    print('Finished writing file: '+fname)
    return


def helpdesk(user, rootdir, fname, project):
    ''' Send e-mail and synda request to helpdesk '''
    msg = MIMEMultipart()
    msg['From'] = user+'@nci.org.au'
    msg['To'] = 'help@nf.nci.org.au'
    #msg['To'] = 'paolap@utas.edu.au'
    msg['Subject'] = 'Synda request: ' + fname
    #message = project + " synda download requested from user: " + user
    message = project + " synda download requested from user: " + user + "\n This is a test message for Kate"
    msg.attach(MIMEText(message, 'plain'))
    f = open(rootdir + fname)
    attachment=MIMEText(f.read())
    f.close()
    attachment.add_header('Content-Disposition','attachement', filename=fname)
    msg.attach(attachment)
    try:
       smtpObj = smtplib.SMTP('localhost')
       smtpObj.sendmail(msg['From'],msg['To'],msg.as_string())        
       print( "Successfully sent email")
    except SMTPException:
       print("Error: unable to send email")
    return


def search_queuee(qm):
    ''' search missing dataset ids in download queuee '''
    # CMIP6 index url
    url = 'http://atlantis.nci.org.au/~kxs900/cmip_index/index_CMIP6.htm'
    # open url
    r =requests.get(url=url)
    # parse url response
    soup = BeautifulSoup(r.content,'html.parser')
    # open dictionary to store results
    status = {}
    # retrieve from table in response the missing dataset_ids
    for q in qm:
        td = soup.table.find('td',string=re.compile(".*" + q[0] + ".*"))
        if td:
            status[q[0]] = td.find_next_sibling()
    td = soup.table.find('td',string=re.compile(".*CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.cl.gr.v20180626*"))
    if td:
        status['CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.cl.gr.v20180626 '] = td.find_next_sibling().text
    if len(status) > 0:
        print("The following datasets are not yet available in the database, but they have been requested or recently downloaded")
        for k,v in status.items():
            print(k + 'status: ' + v)
    return

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
import itertools 


def write_request(project, missing):
    ''' write missing dataset_ids to file to create download request for synda '''
    current_dir = os.getcwd() + '/'
    user = os.environ['USER']
    tstamp = datetime.now().strftime("%Y%m%dT%H%M%S") 
    fname = "_".join([project,user,tstamp])+".txt" 
    f = open(current_dir+fname, 'w')
    variables=set()
    for did in missing:
        f.write('dataset_id='+did[0]+'\n')
        if did[1] != "": variables.add(did[1])
    if len(variables) > 0:
        f.write(" ".join(['variable='] + list(variables)))
    f.close()
    print('\nFinished writing file: '+fname)
    answer = input('Do you want to proceed with request for missing files? (N/Y)\n No is default\n')
    if answer  in ['Y','y','yes','YES']:
        helpdesk(user, current_dir, fname, project)
    else:
        print(f'Your request has been saved in \n {current_dir}/{fname}')
        print('You can always use this file to request the data via the NCI helpdesk: help@nci.org.au  or https://help.nci.org.au.')
    return


def helpdesk(user, rootdir, fname, project):
    ''' Send e-mail and synda request to helpdesk '''
    msg = MIMEMultipart()
    msg['From'] = user+'@nci.org.au'
    msg['To'] = 'help@nf.nci.org.au'
    msg['Subject'] = 'Synda request: ' + fname
    message = project + " synda download requested from user: " + user
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


def search_queue(qm, project, varlist):
    ''' search missing dataset ids in download queue '''
    # CMIP5/CMIP6 index url
    url = 'http://atlantis.nci.org.au/~kxs900/cmip_index/index_'+project+'.htm'
    # open url
    r =requests.get(url=url)
    # parse url response
    soup = BeautifulSoup(r.content,'html.parser')
    # open dictionary to store results
    status = {}
    # retrieve from table in response the missing dataset_ids
    for q in qm:
        td = soup.table.find('td',string=re.compile(".*" + q[0] + ".*"))
        # if CMIP5 you need to match also the variable
        if td:
            if project == "CMIP5" and varlist != []:
                variable=td.find_previous_siblings()[-1].text
                if variable[:-1] not in varlist:
                    continue 
                status[(q[0],variable[:-1])] = td.find_next_sibling()
            else:
                status[(q[0],"")] = td.find_next_sibling()
    if len(status) > 0:
        print("\nThe following datasets are not yet available in the database, but they have been requested or recently downloaded")
        for k,v in status.items():
            print("  ".join([k[0],k[1],'status:',v.text.split(",")[0]]))
    #queued = [k.strip() for k in status.keys()]
    if project == 'CMIP5' and varlist != []:
        # this combines every dataset_id with all the variables, returns (did,var) tuples
        combs = [x for x in itertools.product([q[0] for q in qm], varlist)]
        missing = [x for x in combs if x not in status.keys()] 
    else:
        missing = [(q[0],"") for q in qm if (q[0],"") not in status.keys()] 
    return missing

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
import itertools 
import csv
import platform


def write_request(project, missing):
    ''' write missing dataset_ids to file to create download request for synda '''
    current_dir = os.getcwd() + '/'
    user = os.environ['USER']
    tstamp = datetime.now().strftime("%Y%m%dT%H%M%S") 
    fname = "_".join([project,user,tstamp])+".txt" 
    f = open(current_dir+fname, 'w')
    variables=set()
    for m in missing:
        if project == 'CMIP5':
            did,var = m.split("  ")
            variables.add(var)
        else:
            did = m
        f.write('dataset_id='+did+'\n')
    if len(variables) > 0:
        f.write(" ".join(['variable='] + list(variables)))
    f.close()
    print('\nFinished writing file: '+fname)
    answer = input('Do you want to proceed with request for missing files? (N/Y)\n No is default\n')
    if answer  in ['Y','y','yes','YES'] and platform.node()[0:3] == 'vdi':
        helpdesk(user, current_dir, fname, project)
    else:
        print(f'Your request has been saved in \n {current_dir}/{fname}')
        print('You can always use this file to request the data via the NCI helpdesk: help@nci.org.au  or https://help.nci.org.au.')
    return


def helpdesk(user, rootdir, fname, project):
    ''' Send e-mail and synda request to helpdesk '''
    msg = MIMEMultipart()
    msg['From'] = user+'@nci.org.au'
    #msg['To'] = 'help@nf.nci.org.au'
    msg['To'] = 'paolap@utas.edu.au'
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

def search_queue_csv(qm, project, varlist):
    ''' search missing dataset ids in download queue '''
    rows={}
    dids=set()
    # open csv file and read data in dictionary with dataset_id as key 
    with open("/g/data/ua8/Download/CMIP6/" + project + "_clef_table.csv","r") as csvfile:
        table_read = csv.reader(csvfile)
     # for each row save did-var (to distinguish CMIP5) and separate set of unique dids
        for row in table_read:
            rows[(row[1],row[0])] = row[2]
            dids.add(row[1])
    # retrieve from table the missing dataset_ids
    queued={}
    for q in qm:
        if q[0].replace('ouput.','output1.') in dids:
            did = q[0]
        # if CMIP5 you need to match also the variable
            if project == "CMIP5" and varlist != []:
                queued.update({k[0]+" "+k[1]: v for k,v in rows.items() if k[0]==did and k[1] in varlist})
                #if rows[did][0] not in varlist:
                #    continue
                #else:
                #    queued[did + "  " + rows[did][0]] = rows[did][1]
            else:
                queued.update({k[0]+" "+k[1]: v for k,v in rows.items() if k[0]==did})
                #queued[did] = rows[did][1]

    if len(queued) > 0:
        print("\nThe following datasets are not yet available in the database, but they have been requested or recently downloaded")
        for did,status in queued.items():
            print(" ".join([did,'status:',status]))
    if project == 'CMIP5' and varlist != []:
        # this combines every dataset_id with all the variables, returns a list of "did  var" strings
        combs = [x[0]+" "+x[1] for x in itertools.product([q[0] for q in qm], varlist)]
        missing = [x for x in combs if x not in queued] 
    else:
        missing = [q[0] for q in qm if q[0] not in queued] 
    return missing


Other features
--------------

CSV file output
~~~~~~~~~~~~~~~

The ``--csv`` option added to the command line will output the query
results in a csv file. Rather than getting only the files path, it will
list all the available attributes. This currently works only with the
``--local`` and ``--remote`` option, it doesn’t yet work for the
standard search, which is basically a combination of the two.

.. code::

    !clef --local cmip5 -v pr -v tas -e piControl  -en r1i1p1 -t Amon --csv

.. parsed-literal::

    /g/data/al33/replicas/CMIP5/combined/BCC/bcc-csm1-1-m/piControl/mon/atmos/Amon/r1i1p1/v20120705/pr
    /g/data/al33/replicas/CMIP5/combined/BCC/bcc-csm1-1/piControl/mon/atmos/Amon/r1i1p1/v1/pr
    ...
    /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/piControl/mon/atmos/Amon/r1i1p1/files/tas_20110518
    /g/data/rr3/publications/PMIP3/output/UNSW/CSIRO-Mk3L-1-2/piControl/mon/atmos/Amon/r1i1p1/files/tas_20170728
    /g/data/rr3/publications/PMIP3/output/UNSW/CSIRO-Mk3L-1-2/piControl/mon/atmos/Amon/r1i1p1/v20170728/tas
    Saving to CMIP5_query.csv


.. code::

    !head -n 4 CMIP5_query.csv

.. parsed-literal::

    ,model,experiment,frequency,ensemble,cmor_table,version,variable,path,fdate,tdate,time_complete
    0,BCC-CSM1.1(m),piControl,mon,r1i1p1,Amon,20120705,pr,/g/data/al33/replicas/CMIP5/combined/BCC/bcc-csm1-1-m/piControl/mon/atmos/Amon/r1i1p1/v20120705/pr,101,40012,
    1,BCC-CSM1.1,piControl,mon,r1i1p1,Amon,1,pr,/g/data/al33/replicas/CMIP5/combined/BCC/bcc-csm1-1/piControl/mon/atmos/Amon/r1i1p1/v1/pr,101,50012,
    2,BNU-ESM,piControl,mon,r1i1p1,Amon,20120626,pr,/g/data/al33/replicas/CMIP5/combined/BNU/BNU-ESM/piControl/mon/atmos/Amon/r1i1p1/v20120626/pr,14500101,20081231,True


In the first example I am passing ``--csv`` to a CMIP5 query with the
``--local`` option set. I am hiding the cell output but the tool still
prints the results on the display as well as creating the csv file. The
following example demonstrate how ``--csv`` works also for remote CMIP6
queries and with the flag ``--and`` which allows for more complex
filtering of the data and that we haven’t looked at yet.

.. code::

    !clef --remote cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id --csv


.. parsed-literal::

    ACCESS-CM2 / r1i1p1f1 versions: v20191112
    ACCESS-ESM1-5 / r1i1p1f1 versions: v20191214
    AWI-ESM-1-1-LR / r1i1p1f1 versions: v20200212
    ...
    NorESM2-MM / r1i1p1f1 versions: v20191108
    SAM0-UNICON / r1i1p1f1 versions: v20190910
    TaiESM1 / r1i1p1f1 versions: v20200302, v20200211
    Saving to CMIP6_query.csv

.. code::

    !head -n 4 CMIP6_query.csv

.. parsed-literal::

    ,index,version,activity_id,dataset_id,experiment_id,frequency,grid,grid_label,member_id,nominal_resolution,source_id,source_type,sub_experiment_id,table_id,variable_id,score,comb
    0,0,"('v20200211',)",CMIP,CMIP6.CMIP.AS-RCEC.TaiESM1.piControl.r1i1p1f1.Amon.pr.gn.v20200211|esgf.rcec.sinica.edu.tw,piControl,mon,finite-volume grid with 0.9x1.25 degree lat/lon resolution,gn,r1i1p1f1,100 km,TaiESM1,AOGCM,none,Amon,pr,1.0,"('pr',)"
    1,1,"('v20200211',)",CMIP,CMIP6.CMIP.AS-RCEC.TaiESM1.piControl.r1i1p1f1.Amon.pr.gn.v20200211|esgf.rcec.sinica.edu.tw,piControl,mon,finite-volume grid with 0.9x1.25 degree lat/lon resolution,gn,r1i1p1f1,100 km,TaiESM1,AOGCM,none,Amon,pr,1.0,"('pr',)"
    2,2,"('v20200211',)",CMIP,CMIP6.CMIP.AS-RCEC.TaiESM1.piControl.r1i1p1f1.Amon.pr.gn.v20200211|esgf.rcec.sinica.edu.tw,piControl,mon,finite-volume grid with 0.9x1.25 degree lat/lon resolution,gn,r1i1p1f1,100 km,TaiESM1,AOGCM,none,Amon,pr,1.0,"('pr',)"


Query summary option
~~~~~~~~~~~~~~~~~~~~

The ``--stats`` option added to the command line will print a summary of
the query results It works for both ``--local`` and ``--remote``
options, but not with the default query. Currently it prints the
following: \* total number of models, followed by their names \* total
number of unique model-ensembles/members combinations \* number of
models that have N ensembles/members, followed by their names

.. code::

    !clef --local cmip5 -v pr -e rcp85 -t Amon --stats

.. parsed-literal::
    
    Query summary
    
    42 model/s are available:
    ACCESS1.0 ACCESS1.3 BCC-CSM1.1 BCC-CSM1.1(m) BNU-ESM CCSM4 CESM1(BGC) CESM1(CAM5) CESM1(WACCM) CMCC-CESM CMCC-CM CMCC-CMS CNRM-CM5 CSIRO-Mk3.6.0 CanESM2 EC-EARTH FGOALS-s2 FGOALS_g2 FIO-ESM GFDL-CM3 GFDL-ESM2G GFDL-ESM2M GISS-E2-H GISS-E2-H-CC GISS-E2-R GISS-E2-R-CC HadGEM2-AO HadGEM2-CC HadGEM2-ES IPSL-CM5A-LR IPSL-CM5A-MR IPSL-CM5B-LR MIROC-ESM MIROC-ESM-CHEM MIROC5 MPI-ESM-LR MPI-ESM-MR MRI-CGCM3 MRI-ESM1 NorESM1-M NorESM1-ME inmcm4 
    
    A total of 100 unique model-member combinations are available.
    
      26 model/s have 1 member/s:
    
         ACCESS1.0: r1i1p1
         ACCESS1.3: r1i1p1
         BCC-CSM1.1: r1i1p1
         ...
         NorESM1-ME: r1i1p1
         inmcm4: r1i1p1
    
      7 model/s have 3 member/s:
    
         CESM1(CAM5): r1i1p1, r2i1p1, r3i1p1
         CESM1(WACCM): r2i1p1, r3i1p1, r4i1p1
         FGOALS-s2: r1i1p1, r2i1p1, r3i1p1
         FIO-ESM: r1i1p1, r2i1p1, r3i1p1
         HadGEM2-CC: r1i1p1, r2i1p1, r3i1p1
         MIROC5: r1i1p1, r2i1p1, r3i1p1
         MPI-ESM-LR: r1i1p1, r2i1p1, r3i1p1
    
      2 model/s have 4 member/s:
    
         HadGEM2-ES: r1i1p1, r2i1p1, r3i1p1, r4i1p1
         IPSL-CM5A-LR: r1i1p1, r2i1p1, r3i1p1, r4i1p1
    
      4 model/s have 5 member/s:
    
         CNRM-CM5: r10i1p1, r1i1p1, r2i1p1, r4i1p1, r6i1p1
         CanESM2: r1i1p1, r2i1p1, r3i1p1, r4i1p1, r5i1p1
         GISS-E2-H: r1i1p1, r1i1p2, r1i1p3, r2i1p1, r2i1p3
         GISS-E2-R: r1i1p1, r1i1p2, r1i1p3, r2i1p1, r2i1p3
    
      1 model/s have 6 member/s:
    
         CCSM4: r1i1p1, r2i1p1, r3i1p1, r4i1p1, r5i1p1, r6i1p1
    
      1 model/s have 9 member/s:
    
         EC-EARTH: r11i1p1, r12i1p1, r13i1p1, r1i1p1, r2i1p1, r6i1p1, r7i1p1, r8i1p1, r9i1p1
    
      1 model/s have 10 member/s:
    
         CSIRO-Mk3.6.0: r10i1p1, r1i1p1, r2i1p1, r3i1p1, r4i1p1, r5i1p1, r6i1p1, r7i1p1, r8i1p1, r9i1p1
    

Errata and ESDOC
~~~~~~~~~~~~~~~~

Another new features are functions that retrieve errata associated to a
file and the documents available in the ESDOC system. We are still
working to make these accessible from the command line and also to add
tracking_ids to our query outputs. In the meantime you can load them and
use them after having retrieve the tracking_id attribute in another way
(for example with a simple nc_dump or via xarray if in python). Let’s
start from the errata:

.. code::

    from clef.esdoc import *
    tracking_id = 'hdl:21.14100/a2c2f719-6790-484b-9f66-392e62cd0eb8'
    error_ids = errata(tracking_id)
    for eid in error_ids:
        print_error(eid)


.. parsed-literal::

    You can view the full report online:
    https://errata.es-doc.org/static/view.html?uid=99f28ccc-53b3-68dc-8fb1-f7ca4a2d3393
    Title: pr and prc have incorrect values at daily and monthly timescales due to an incorrect scaling factor
    Status: resolved
    Description: Within the conversion from CESM's CAM precipitation units (m s-1) to CMIP's units of (kg m-2 s-1) an incorrect scaling factor was applied. The conversion should have been to multiply CAM's values by 1000 kg m-3. Instead, the values were multiplied by 1000 and then divided by 86400, resulting in values that are too small.


As you can see I’ve chosen a tracking_id that was associated to some
errata. First I use the **errata()** function to retrieve any associated
error_ids and then I print out the result using the **print_error()**
function. This first retrieve the message associated to any error_id and
then prints it in a human readable form, including the url for the
original error report. Let’s now have a look at how to retrieve and
print some documentation from ESDOC.

.. code::

    doc_url = get_doc(dtype='model', name='MIROC6', project='CMIP6')


.. parsed-literal::

    MIP Era > CMIP6
    Institute > MIROC
    Canonical Name > --
    Name > MIROC6
    Type > GCM
    Long Name > --
    Overview > --
    Keywords > --
    name > MIROC6
    keywords > CCSR-AGCM, SPRINTARS, COCO, MATSIRO, atmosphere, aerosol, sea-ice ocean, land surface
    overview > MIROC6 is a physical climate model mainly composed of three sub-models: atmosphere, land, and sea ice....


This time we can use directly one function **get_doc()**. It gets three
arguments: \* the kind of document, can be model, experiment or mip; \*
the name of the model, experiment or mip; \* project for which I want to
retrieve the document, by default this is CMIP6. It will retrieve the
document online and print out a summary. It will also return the url for
the full document report, shown below.

.. code::

    print(doc_url)

.. parsed-literal::

    https://api.es-doc.org/2/document/search-name?client=ESDOC-VIEWER-DEMO&encoding=html&project=CMIP6&name=MIROC6&type=CIM.2.SCIENCE.MODEL


ESDOC works only for CMIP6 and newer ESGF datasets. The World data
Center for Climate (WDCC) website holds documentation for both CMIP6 and
CMIP5, the **get_wdcc()** function access these documents. In this case
rather than the type of document you have to use the dataset_id to
retrieve the information.

.. code::

    doc_url, response = get_wdcc('cmip5.output1.MIROC.MIROC5.historical.mon.atmos.Amon.r1i1p1.v20111028')
    print(doc_url)
    print(response.text)


.. parsed-literal::

    https://cera-www.dkrz.de/WDCC/ui/cerasearch/solr/select?rows=1&wt=json&q=entry_name_s:cmip5*output1*MIROC*MIROC5
    {"responseHeader":{"status":0,"QTime":4,"params":{"q":"entry_name_s:cmip5*output1*MIROC*MIROC5","rows":"1","wt":"json"}},"response":{"numFound":1,"start":0,"maxScore":1,"docs":[{"geo":["ENVELOPE(-180.00, 180.00, 90.00,-90.00)"],"accuracy_report_s":"not filled","specification_s":"not filled","completeness_report_s":"not filled","entry_type_s":"experiment","qc_institute_s":"MIROC","summary_s":"MIROC data of the MIROC5 model as contribution for CMIP5 - Coupled Model\nIntercomparison Project Phase 5 (https://pcmdi.llnl.gov/mips/cmip5).\nExperiment design is described in detail in\nhttps://pcmdi.llnl.gov/mips/cmip5/experiment_design.html and the list of output\nvariables and their temporal resolutions are given in\nhttps://pcmdi.llnl.gov/mips/cmip5/datadescription.html . The output is stored in netCDF\nformat as time series per variable in model grid spatial resolution. For more information\non the Earth System model and the simulation please refer to the CIM repository.","general_key_ss":["CMIP5","IPCC","IPCC-AR5","IPCC-DDC","MIROC5","climate simulation"],"entry_name_s":"cmip5 output1 MIROC MIROC5","textSuggest":["cmip5 output1 MIROC MIROC5","IPCC-AR5_CMIP5","MIM5","IPCC-AR5_CMIP5 (IPCC Assessment Report 5 and Coupled Model Intercomparison Project data sets)"],"title_sort":"cmip5 output1 MIROC MIROC5","date_range_rdt":"[1960-01 TO 2669-12]","progress_acronym_s":"completely archived","consistency_report_s":"not filled","additional_infos_ss":["standard_output.pdf","Taylor_CMIP5_design.pdf"],"creation_date_dt":"2012-01-13T14:54:16Z","project_acronym_ss":["IPCC-AR5_CMIP5"],"authors_s":"MIROC","model_s":"MIROC5","id":"2320274","entry_acronym_s":"MIM5","project_name_ss":["IPCC-AR5_CMIP5 (IPCC Assessment Report 5 and Coupled Model Intercomparison Project data sets)"],"hierarchy_steps_ss":["IPCC-AR5_CMIP5","MIM5"],"access_s":"http://cera-www.dkrz.de/WDCC/CMIP5/Compact.jsp?acronym=MIM5","hierarchy_ss":["project @ 2 @ IPCC-AR5_CMIP5 @"],"_version_":1698339380635107300,"score":1}]},"spellcheck":{"suggestions":[],"correctlySpelled":true,"collations":[]}}


We are still working to add a function that will give a formatted print
of the wdcc documents as for the the ESDOC ones.

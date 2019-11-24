
New features
------------

We recently added new output features following a user request. These
are currently only available in the analysis3-unstable environment::

     $ module load conda/analysis3-unstable

CSV file output
~~~~~~~~~~~~~~~

The *–csv* option added to the command line will output the query
results in a csv file. rather than getting only the files path, it will
list all the available attributes. This currently works only with the
*–local* option, it doesn’t yet work for the standard search or remote.
These last both perform an ESGF query rather than searching directly the
MAS database as *local* so they need to be treated differently. We are
still working on this.::

    !clef --local cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id --csv


    BCC-CSM2-MR r1i1p1f1 {'v20181016', 'v20181012'}
    BCC-ESM1 r1i1p1f1 {'v20181211', 'v20181214'}
    ...
    NorESM2-LM r1i1p1f1 {'v20190815'}
    SAM0-UNICON r1i1p1f1 {'v20190910'}

::

    !head -n 3 CMIP6_query.csv

    activity_id,source_id,source_type,experiment_id,sub_experiment_id,frequency,r,i,p,f,variant_label,member_id,variable_id,grid_label,nominal_resolution,table_id,version,variable,pdir,fdate,tdate,time_complete
    CMIP,BCC-CSM2-MR,AOGCM,piControl,none,mon,1,1,1,1,r1i1p1f1,r1i1p1f1,pr,gn,100 km,Amon,v20181016,pr,/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Amon/pr/gn/v20181016,18500101,24491231,True
    CMIP,BCC-ESM1,AER AOGCM BGC,piControl,none,mon,1,1,1,1,r1i1p1f1,r1i1p1f1,pr,gn,250 km,Amon,v20181214,pr,/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-ESM1/piControl/r1i1p1f1/Amon/pr/gn/v20181214,18500101,23001231,True
    

Query summary option
~~~~~~~~~~~~~~~~~~~~

The *–stats* option added to the command line will print a summary of
the query results It works for both *–local* and *–remote* options, but
not with the default query. Currently it prints the following: \* total
number of models, followed by their names \* total number of unique
model-ensembles/members combinations \* number of models that have N
ensembles/members, followed by their names::

    !clef --local cmip5 -v pr -v mrso -e piControl --frequency mon --stats

    
    Query summary
    
    48 model/s are available:
    ACCESS1.0 ACCESS1.3 BCC-CSM1.1 BCC-CSM1.1(m) BNU-ESM CCSM4 CESM1(BGC) CESM1(CAM5) CESM1(WACCM) CESM1-CAM5.1-FV2 CESM1-FASTCHEM CMCC-CESM CMCC-CM CMCC-CMS CNRM-CM5 CNRM-CM5-2 CSIRO-Mk3.6.0 CSIRO-Mk3L-1-2 CanESM2 EC-EARTH FGOALS-g2 FGOALS-s2 FGOALS_g2 FIO-ESM GFDL-CM3 GFDL-ESM2G GFDL-ESM2M GISS-E2-H GISS-E2-H-CC GISS-E2-R GISS-E2-R-CC HadGEM2-AO HadGEM2-CC HadGEM2-ES IPSL-CM5A-LR IPSL-CM5A-MR IPSL-CM5B-LR MIROC-ESM MIROC-ESM-CHEM MIROC4h MIROC5 MPI-ESM-LR MPI-ESM-MR MPI-ESM-P MRI-CGCM3 NorESM1-M NorESM1-ME inmcm4 
    
    A total of 59 unique model-member combinations are available.
    
    44 model/s have 1 member/s:
    ACCESS1.0 ACCESS1.3 BCC-CSM1.1 BCC-CSM1.1(m) BNU-ESM CESM1(BGC) CESM1(CAM5) CESM1(WACCM) CESM1-CAM5.1-FV2 CESM1-FASTCHEM CMCC-CESM CMCC-CM CMCC-CMS CNRM-CM5 CSIRO-Mk3.6.0 CSIRO-Mk3L-1-2 CanESM2 EC-EARTH FGOALS-g2 FGOALS-s2 FGOALS_g2 FIO-ESM GFDL-CM3 GFDL-ESM2G GFDL-ESM2M GISS-E2-H-CC GISS-E2-R-CC HadGEM2-AO HadGEM2-CC HadGEM2-ES IPSL-CM5A-LR IPSL-CM5A-MR IPSL-CM5B-LR MIROC-ESM MIROC-ESM-CHEM MIROC4h MIROC5 MPI-ESM-LR MPI-ESM-MR MPI-ESM-P MRI-CGCM3 NorESM1-M NorESM1-ME inmcm4 
    
    2 model/s have 3 member/s:
    CCSM4 GISS-E2-H 
    
    1 model/s have 4 member/s:
    CNRM-CM5-2 
    
    1 model/s have 5 member/s:
    GISS-E2-R 


Errata and ESDOC
~~~~~~~~~~~~~~~~

Another new features are functions that retrieve errata associated to a
file and the documents available in the ESDOC system. We are still
working to make these accessible from the command line and also to add
tracking_ids to our query outputs. In the meantime you can load them and
use them after having retrieve the tracking_id attribute in another way
(for example with a simple nc_dump or via xarray if in python). Let’s
start from the errata:::

    from clef.esdoc import *
    tracking_id = 'hdl:21.14100/a2c2f719-6790-484b-9f66-392e62cd0eb8'
    error_ids = errata(tracking_id)
    for eid in error_ids:
        print_error(eid)


    You can view the full report online:
    https://errata.es-doc.org/static/view.html?uid=99f28ccc-53b3-68dc-8fb1-f7ca4a2d3393
    Title: pr and prc have incorrect values at daily and monthly timescales due to an incorrect scaling factor
    Status: resolved
    Description: Within the conversion from CESM's CAM precipitation units (m s-1) to CMIP's units of (kg m-2 s-1) an incorrect scaling factor was applied. The conversion should have been to multiply CAM's values by 1000 kg m-3. Instead, the values were multiplied by 1000 and then divided by 86400, resulting in values that are too small.


As you can see I’ve chosen a tracking_id that was associated to some
errata. First I use the **errata()** function to retrieve any associated
error_ids and then I print out the result using the **print_error()**
function. This first retrieve the message associted to any error_id and
then prints it in a human readable form, including the url for the
original error report. Let’s now have a look at how to retrieve and
print some documentation from ESDOC.::

    doc_url = get_doc(dtype='model', name='MIROC6', project='CMIP6')


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
    overview > MIROC6 is a physical climate model mainly composed of ...
    flux correction - details > No flux corrections are applied in this model.
    ...
    snow processes - has snow ice formation > True
    snow processes - snow ice formation scheme > When snow-ice interface comes below sea level, the snow between the interface and sea level turns into sea ice.
    snow processes - redistribution > Snow-ice
    surface albedo > Other

NB we cut down the output since the document is really long!

This time we can use directly one function **get_doc()**. It gets three
arguments: \* the kind of document, can be model, experiment or mip; \*
the name of the model, experiment or mip; \* project for which I want to
retrieve the document, by default this is CMIP6. It will retrieve the
document online and print out a summary. It will also return the url for
the full document report, shown below.::

    print(doc_url)


    https://api.es-doc.org/2/document/search-name?client=ESDOC-VIEWER-DEMO&encoding=html&project=CMIP6&name=MIROC6&type=CIM.2.SCIENCE.MODEL


ESDOC works only for CMIP6 and newer ESGF datasets. The World data
Center for Climate (WDCC) website holds documentation for both CMIP6 and
CMIP5, the **get_wdcc()** function access these documents. In this case
rather than the type of document you have to use the datset_id to
retrieve the information.::

    doc_url, response = get_wdcc('cmip5.output1.MIROC.MIROC5.historical.mon.atmos.Amon.r1i1p1.v20111028')
    print(doc_url)
    print(response['response']['docs'])


    https://cera-www.dkrz.de/WDCC/ui/cerasearch/solr/select?rows=1&wt=json&q=entry_name_s:cmip5*output1*MIROC*MIROC5
    [{'geo': ['ENVELOPE(-180.00, 180.00, 90.00,-90.00)'], 'accuracy_report_s': 'not filled', 'specification_s': 'not filled', 'completeness_report_s': 'not filled', 'entry_type_s': 'experiment', 'qc_institute_s': 'MIROC', 'summary_s': 'MIROC data of the MIROC5 model as contribution for CMIP5 - Coupled Model\nIntercomparison Project Phase 5 (https://pcmdi.llnl.gov/mips/cmip5).\nExperiment design is described in detail in\nhttps://pcmdi.llnl.gov/mips/cmip5/experiment_design.html and the list of output\nvariables and their temporal resolutions are given in\nhttps://pcmdi.llnl.gov/mips/cmip5/datadescription.html . The output is stored in netCDF\nformat as time series per variable in model grid spatial resolution. For more information\non the Earth System model and the simulation please refer to the CIM repository.', 'general_key_ss': ['CMIP5', 'IPCC', 'IPCC-AR5', 'IPCC-DDC', 'MIROC5', 'climate simulation'], 'entry_name_s': 'cmip5 output1 MIROC MIROC5', 'date_range_rdt': '[1960-01 TO 2669-12]', 'progress_acronym_s': 'completely archived', 'consistency_report_s': 'not filled', 'additional_infos_ss': ['standard_output.pdf', 'Taylor_CMIP5_design.pdf'], 'creation_date_dt': '2012-01-13T14:54:16Z', 'project_acronym_ss': ['IPCC-AR5_CMIP5'], 'authors_s': 'MIROC', 'model_s': 'MIROC5', 'id': '2320274', 'entry_acronym_s': 'MIM5', 'project_name_ss': ['IPCC-AR5_CMIP5 (IPCC Assessment Report 5 and Coupled Model Intercomparison Project data sets)'], 'hierarchy_steps_ss': ['IPCC-AR5_CMIP5', 'MIM5'], 'access_s': 'http://cera-www.dkrz.de/WDCC/CMIP5/Compact.jsp?acronym=MIM5', 'hierarchy_ss': ['project @ 2 @ IPCC-AR5_CMIP5 @ '], '_version_': 1650056364700991488, 'score': 1.0}]


We are still working to add a function that will give a formatted print
of the wdcc documents as for the the ESDOC ones.

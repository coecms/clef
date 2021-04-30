CORDEX
------

.. code:: ipython3

    !clef cordex --help

.. parsed-literal::

    Usage: clef cordex [OPTIONS] [QUERY]...
    
      Search ESGF and local database for CORDEX files.
    
      Constraints can be specified multiple times, in which case they are
      combined    using OR: -v tas -v tasmin will return anything matching
      variable = 'tas' or variable = 'tasmin'. The --latest flag will check ESGF
      for the latest version available, this is the default behaviour NB. for
      CORDEX data associated to CMIP6 use  the cmip6 command with CORDEX as
      activity_id
    
    Options:
      --latest / --all-versions       Return only the latest version or all of
                                      them. Default: --latest
    
      --replica / --no-replica        Return both original files and replicas.
                                      Default: --no-replica
    
      --distrib / --no-distrib        Distribute search across all ESGF nodes.
                                      Default: --distrib
    
      --csv / --no-csv                Send output to csv file including extra
                                      information. Works only with --local and
                                      --remote. Default: --no-csv
    
      --stats / --no-stats            Write summary of query results. Works only
                                      with --local and --remote. Default: --no-
                                      stats
    
      --debug / --no-debug            Show debug output. Default: --no-debug
      -d, --domain FACET              CORDEX region name
      -e, --experiment FACET          Experiment
      -dex, --driving_experiment FACET
                                      CMIP5 experiment of driving GCM or
                                      'evaluation' for re-analysis
    
      -dmod, --driving_model FACET    Model/analysis used to drive the model (eg.
                                      ECMWF­ERAINT)
    
      -m, --rcm_name FACET            Identifier of the CORDEX Regional Climate
                                      Model
    
      -rcmv, --rcm_version FACET      Identifier for reruns with perturbed
                                      parameters or smaller RCM release upgrades
    
      -v, --variable FACET            Variable name in file
      -f, --time_frequency FACET      Output frequency indicator
      -en, --ensemble FACET           Ensemble member of the driving GCM
      -vrs, --version FACET           Data publication version
      -cf, --cf_standard_name FACET   CF-Conventions name of the variable
      -ef, --experiment_family FACET  Experiment family: All, Historical, RCP
      -inst, --institute FACET        identifier for the institution that is
                                      responsible for the scientific aspects of
                                      the CORDEX simulation
    
      --and [domain|experiment|driving_experiment|driving_model|rcm_name|rcm_version|variable|time_frequency|ensemble|version|cf_standard_name|experiment_family|institute]
                                      Attributes for which we want to add AND
                                      filter, i.e. -v tasmin -v tasmax --and
                                      variable will return only model/ensemble
                                      that have both
    
      --help                          Show this message and exit.


**cordex** works in the same way but some constraints are specific to
its experiment design. These are the cordex ``domain``, ``rcm_name``,
``rcm_version`` for the regional model, and the ``driving_model`` and
``driving_experiment`` for the driving model. CORDEX also does not use
tables so you always have to use f\ ``--frequency`` to select different
timesteps.

.. code:: ipython3

    !clef cordex -v tas -e historical -dmod CSIRO-BOM-ACCESS1-3 -en r1i1p1 -f mon


.. parsed-literal::

    /g/data/rr3/publications/CORDEX/output/AUS-44/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360J/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360K/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360L/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44i/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360J/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44i/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360K/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44i/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360L/v1/mon/tas/latest/
    
    Everything available on ESGF is also available locally


CMIP6
-----

.. code:: ipython3

    !clef cmip6 --help


.. parsed-literal::

    Usage: clef cmip6 [OPTIONS] [QUERY]...
    
      Search ESGF and local database for CMIP6 files Constraints can be
      specified multiple times, in which case they are combined using OR:  -v
      tas -v tasmin will return anything matching variable = 'tas' or variable =
      'tasmin'. The --latest flag will check ESGF for the latest version
      available, this is the default behaviour
    
    Options:
      -mip, --activity [AerChemMIP|C4MIP|CDRMIP|CFMIP|CMIP|CORDEX|DAMIP|DCPP|DynVarMIP|FAFMIP|GMMIP|GeoMIP|HighResMIP|ISMIP6|LS3MIP|LUMIP|OMIP|PAMIP|PMIP|RFMIP|SIMIP|ScenarioMIP|VIACSAB|VolMIP]
      -e, --experiment x              CMIP6 experiment, list of available depends
                                      on activity
    
      --source_type [AER|AGCM|AOGCM|BGC|CHEM|ISM|LAND|OGCM|RAD|SLAB]
      -t, --table x                   CMIP6 CMOR table: Amon, SIday, Oday ...
      -m, --model, --source_id x      CMIP6 model id: GFDL-AM4, CNRM-CM6-1 ...
      -v, --variable x                CMIP6 variable name as in filenames
      -mi, --member TEXT              CMIP6 member id: <sub-exp-id>-r#i#p#f#
      -g, --grid, --grid_label TEXT   CMIP6 grid label: i.e. gn for the model
                                      native grid
    
      -nr, --resolution, --nominal_resolution TEXT
                                      Approximate resolution: '250 km', pass in
                                      quotes
    
      --frequency [1hr|1hrCM|1hrPt|3hr|3hrPt|6hr|6hrPt|day|dec|fx|mon|monC|monPt|subhrPt|yr|yrPt]
      --realm [aerosol|atmos|atmosChem|land|landIce|ocean|ocnBgchem|seaIce]
      -se, --sub_experiment_id TEXT   Only available for hindcast and forecast
                                      experiments: sYYYY
    
      -vl, --variant_label TEXT       Indicates a model variant: r#i#p#f#
      --cf_standard_name TEXT         CF variable standard_name, use instead of
                                      variable constraint
    
      --and [variable_id|experiment_id|table_id|realm|frequency|member_id|source_id|source_type|activity_id|grid|grid_label|nominal_resolution|sub_experiment_id]
                                      Attributes for which we want to add AND
                                      filter, i.e. `--and variable_id` to apply to
                                      variable values
    
      --cite                          Write list of citations for query results,
                                      works only with --remote and --local
                                      options. Default: False
    
      --institution TEXT              Modelling group institution id: IPSL, NOAA-
                                      GFDL ...
    
      --latest / --all-versions       Return only the latest version or all of
                                      them. Default: --latest
    
      --replica / --no-replica        Return both original files and replicas.
                                      Default: --no-replica
    
      --distrib / --no-distrib        Distribute search across all ESGF nodes.
                                      Default: --distrib
    
      --csv / --no-csv                Send output to csv file including extra
                                      information. Works only with --local and
                                      --remote. Default: --no-csv
    
      --stats / --no-stats            Write summary of query results. Works only
                                      with --local and --remote. Default: --no-
                                      stats
    
      --debug / --no-debug            Show debug output. Default: --no-debug
      --help                          Show this message and exit.


The **cmip6** sub-command works in the same way but some constraints are
different. As well as changes in terminology CMIP6 has more attributes
(*facets*) that can be used to select the data. Examples of these are
the **activity** which groups experiments, **resolution** which is an
approximation of the actual resolution and **grid**.

Controlling the ouput: clef options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    !clef --local cmip6 -e 1pctCO2 -t Amon -v tasmax -v tasmin -g gr


.. parsed-literal::

    /g/data/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1-HR/1pctCO2/r1i1p1f2/Amon/tasmax/gr/v20191021
    /g/data/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/1pctCO2/r1i1p1f2/Amon/tasmax/gr/v20180626
    /g/data/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-ESM2-1/1pctCO2/r10i1p1f2/Amon/tasmax/gr/v20200529
    ...
    /g/data/oi10/replicas/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/1pctCO2/r1i1p1f1/Amon/tasmin/gr/v20180727
    /g/data/oi10/replicas/CMIP6/CMIP/THU/CIESM/1pctCO2/r1i1p1f1/Amon/tasmin/gr/v20200417


In this example we used the ``--local`` option for the main command
**clef** to get only the local matching data path as output. Note also
that: - we are using abbreviations for the options where available; - we
are passing the variable ``-v`` option twice; - we used the CMIP6
specific option ``-g/--grid`` to search for all data that is not on the
model native grid. This doesn’t indicate a grid common to all the CMIP6
output only to the model itself, the same is true for member_id and
other attributes.

``--local`` is actually executing the query directly on the NCI
clef.nci.org.au database, which is different from the default query
where the search is executed first on the ESGF and then its results are
matched locally. In the example above the final result is exactly the
same, whichever way we perform the query. This way of searching can give
you more results if a node is offline or if a version have been
unpublished from the ESGF but is still available locally.

.. code:: ipython3

    !clef --missing cmip6 -e 1pctCO2 -v clw -v clwvi -t Amon -g gr


.. parsed-literal::

    
    Available on ESGF but not locally:
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clw.gr.v20200620
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20200620
    ...
    CMIP6.CMIP.THU.CIESM.1pctCO2.r1i1p1f1.Amon.clw.gr.v20200417
    CMIP6.CMIP.THU.CIESM.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20200417


This time we used the ``--missing`` option and the tool returned only
the results matching the constraints that are available on the ESGF but
not locally (we changed variables to make sure to get some missing data
back).

.. code:: ipython3

    !clef --remote cmip6 -e 1pctCO2 -v tasmin -t Amon -g gr


.. parsed-literal::

    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1-HR.1pctCO2.r1i1p1f2.Amon.tasmin.gr.v20191021
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.tasmin.gr.v20180626
    ...
    CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.tasmin.gr.v20180727
    CMIP6.CMIP.NIMS-KMA.KACE-1-0-G.1pctCO2.r1i1p1f1.Amon.tasmin.gr.v20200115
    CMIP6.CMIP.THU.CIESM.1pctCO2.r1i1p1f1.Amon.tasmin.gr.v20200417


The ``--remote`` option returns the Dataset_ids of the data matching the
constraints, regardless that they are available locally or not.

Please note that ``--local``, ``--remote`` and ``--missing`` together
with ``--request``, which we will look at next, are all options of the
main command **clef** and they need to come before any sub-commands.

Requesting new data
-------------------

What should we do if we found out there is some data we are interested
to that has not been downloaded or requested yet? This is a complex data
collection, NCI, in consultation with the community, decided the best
way to manage it was to have one point of reference. Part of this
agreement is that NCI will download the files and update the database
that **clef** is interrrogating. After consultation with the community a
priority list was decided and NCI has started downloading anything that
falls into it as soon as become available. Users can then request from
the NCI helpdesk, other combinations of variables, experiments etc that
do not fall into this list. The list is available from the NCI climate
confluence website: Even without consulting the list you can use
**clef**, as we demonstrated above, to search for a particular dataset,
if it is not queued or downloaded already **clef** will give you an
option to request it from NCI. Let’s see how it works.

.. code:: bash

    %%bash
    clef --request cmip6 -e 1pctCO2 -v clw -v clwvi -t Amon -g gr
    no


.. parsed-literal::

    
    Available on ESGF but not locally:
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clw.gr.v20200620
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20200620
    ...
    CMIP6.CMIP.THU.CIESM.1pctCO2.r1i1p1f1.Amon.clw.gr.v20200417
    CMIP6.CMIP.THU.CIESM.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20200417
    Do you want to proceed with request for missing files? (N/Y)
     No is default
    Your request has been saved in 
     /home/581/pxp581/clef/docs/CMIP6_pxp581_20210429T135117.txt
    You can use this file to request the data via the NCI helpdesk: help@nci.org.au  or https://help.nci.org.au.


We run the same query which gave us as a result 4 missing datasets but
this time we used the ``--request`` option after **clef**. The tool will
execute the query remotely, then look for matches locally and on the NCI
download list. Having found none gives as an option of putting in a
request. It will accept any of the following as a positive answer: > Y
YES y yes

With anything else or if you don’t pass anything it will assume you
don’t want to put in a request. It still saved the request in a file we
can use later.

.. code:: ipython3

    !head -n 4 CMIP6_*.txt


.. parsed-literal::

    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clw.gr.v20200620
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20200620
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clw.gr.v20200620
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clwvi.gr.v20200620


If I answered **yes** the tool would have sent an e-mail to the NCI
helpdesk with the text file attached, NCI can pass that file as input to
their download tool and queue your request. NB if you are running clef
from gadi you cannot send an e-mail so in that case the tool will skip
the question and just remind you to send an e-mail to the NCI helpdesk
yourself to finalise the request.

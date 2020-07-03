
Using CleF - Climate Finder to discover ESGF data at NCI
========================================================

This notebook shows examples of how to use the CleF (Climate Finder)
python module to search for ESGF data on the NCI server. Currently the
tool is set up for CMIP5 and CMIP6 data, but other ESGF dataset like
CORDEX will be available in the future.

CleF is currently installed in the CMS conda module analysis3. This is
managed by the CMS and is available simply by running::
  $ module use /g/data3/hh5/public/modules
  $ module load conda/analysis3
NB Use "module load conda/analysis3-unstable" for the latest version

You could use the module interactively, for the moment we will use its
command line options. Let’s start!

Command syntax
--------------

.. code:: ipython3

    !clef

.. code:: ipython3

.. parsed-literal::

    Usage: clef [OPTIONS] COMMAND [ARGS]...
    
    Options:
      --remote   returns only ESGF search results
      --local    returns only local files matching arguments in local database
      --missing  returns only missing files matching ESGF search
      --request  send NCI request to download missing files matching ESGF search
      --debug    Show debug info
      --help     Show this message and exit.
    
    Commands:
      cmip5  Search ESGF and local database for CMIP5 files Constraints can be...
      cmip6  Search ESGF and local database for CMIP6 files Constraints can be...
      ds     Search local database for non-ESGF datasets


By simpling running the command **clef** with no arguments, the tool
shows the help message and then exits, basically it is equivalent to >
clef –help

We can see currently there are 3 sub-commands, **ds** to query non-ESGF
collections and one for each cmip dataset: **cmip5** and **cmip6**.
There are also five different options that can be passed before the
sub-commands, one we have already seen is *–help*. The others are used
to modify how the tool will deal with the main query output. We will
have a look at them and at **ds** later. Let’s start from quering some
CMIP5 data, to see what we can pass to the **cmip5** sub-command we can
simply run it with its *–help* option.

CMIP5
-----

::

    !clef cmip5 --help


.. parsed-literal::

    Usage: clef cmip5 [OPTIONS] [QUERY]...
    
      Search ESGF and local database for CMIP5 files
    
      Constraints can be specified multiple times, in which case they are
      combined    using OR: -v tas -v tasmin will return anything matching
      variable = 'tas' or variable = 'tasmin'. The --latest flag will check ESGF
      for the latest version available, this is the default behaviour
    
    Options:
      -e, --experiment x              CMIP5 experiment: piControl, rcp85, amip ...
      --experiment_family [Atmos-only|Control|Decadal|ESM|Historical|Idealized|Paleo|RCP]
                                      CMIP5 experiment family: Decadal, RCP ...
      -m, --model x                   CMIP5 model acronym: ACCESS1.3, MIROC5 ...
      -t, --table, --mip [Amon|Omon|OImon|LImon|Lmon|6hrPlev|6hrLev|3hr|Oclim|Oyr|aero|cfOff|cfSites|cfMon|cfDay|cf3hr|day|fx|grids]
      -v, --variable x                Variable name as shown in filanames: tas,
                                      pr, sic ...
      -en, --ensemble, --member TEXT  CMIP5 ensemble member: r#i#p#
      --frequency [mon|day|3hr|6hr|fx|yr|monClim|subhr]
      --realm [atmos|ocean|land|landIce|seaIce|aerosol|atmosChem|ocnBgchem]
      --and [variable|experiment|cmor_table|realm|time_frequency|model|ensemble]
                                      Attributes for which we want to add AND
                                      filter, i.e. `--and variable` to apply to
                                      variable values
      --institution TEXT              Modelling group institution id: MIROC, IPSL,
                                      MRI ...
      --cf_standard_name TEXT         CF variable standard_name, use instead of
                                      variable constraint
      --format [file|dataset]         Return output for datasets (default) or
                                      individual files
      --latest / --all-versions       Return only the latest version or all of
                                      them. Default: --latest
      --replica / --no-replica        Return both original files and replicas.
                                      Default: --no-replica
      --distrib / --no-distrib        Distribute search across all ESGF nodes.
                                      Default: --distrib
      --csv / --no-csv                Send output to csv file including extra
                                      information. Default: --no-csv
      --stats / --no-stats            Write summary of query results, works only
                                      with --local option. Default: --no-stats
      --debug / --no-debug            Show debug output. Default: --no-debug
      --help                          Show this message and exit.


Passing arguments and options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *help* shows all the constraints we can pass to the tool, there are
also some additional options which can change the way we run our query.
For the moment we can ignore these and use their default values. Some of
the constraints can be passed using an abbreviation,like *-v* instead of
*–variable*. This is handy once you are more familiar with the tool. The
same option can have more than one name, for example *–ensemble* can
also be passed as *–member*, this is because the terminology has changed
between CMIP5 and CMIP6. You can pass how many constraints you want and
pass the same constraint more than once. Let’s see what happens though
if we do not pass any constraint.

:: 

    !clef cmip5


.. parsed-literal::

    Too many results 3766700, try limiting your search:
      https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5


:: 

    !clef cmip5 --variable tasmin --experiment historical --table day --ensemble r2i1p1s


.. parsed-literal::

    No matches found on ESGF, check at https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5&ensemble=r2i1p1s&experiment=historical&cmor_table=day&variable=tasmin


Oops that wasn’t reasonable! I mispelled the ensemble “r2i1p1s” does not
exists and the tool is telling me it cannot find any matches.

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table days --ensemble r2i1p1


.. parsed-literal::

    Usage: clef cmip5 [OPTIONS] [QUERY]...
    Try "clef cmip5 --help" for help.
    
    Error: Invalid value for "--table" / "--mip" / "-t": invalid choice: days. (choose from Amon, Omon, OImon, LImon, Lmon, 6hrPlev, 6hrLev, 3hr, Oclim, Oyr, aero, cfOff, cfSites, cfMon, cfDay, cf3hr, day, fx, grids)


Made another spelling mistake, in this case the tool knows that I passed
a wrong value and lists for me all the available options for the CMOR
table. Eventually we are aiming to validate all the arguments we can,
although for some it is no possible to pass all the possible values
(ensemble for example).

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table day --ensemble r2i1p1


.. parsed-literal::

    None
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/historical/day/atmos/day/r2i1p1/files/tasmin_20110518/
    /g/data1b/al33/replicas/CMIP5/combined/CCCma/CanCM4/historical/day/atmos/day/r2i1p1/v20120207/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/CCCma/CanCM4/historical/day/atmos/day/r2i1p1/v20120612/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/CCCma/CanESM2/historical/day/atmos/day/r2i1p1/v20120410/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/CNRM-CERFACS/CNRM-CM5/historical/day/atmos/day/r2i1p1/v20120703/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/IPSL/IPSL-CM5A-LR/historical/day/atmos/day/r2i1p1/v20130506/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/IPSL/IPSL-CM5A-MR/historical/day/atmos/day/r2i1p1/v20130506/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/LASG-IAP/FGOALS-s2/historical/day/atmos/day/r2i1p1/v20161204/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC-ESM/historical/day/atmos/day/r2i1p1/v20120710/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC4h/historical/day/atmos/day/r2i1p1/v20120628/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/historical/day/atmos/day/r2i1p1/v20120710/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MOHC/HadCM3/historical/day/atmos/day/r2i1p1/v20140110/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MOHC/HadGEM2-CC/historical/day/atmos/day/r2i1p1/v20111129/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MOHC/HadGEM2-ES/historical/day/atmos/day/r2i1p1/v20110418/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MPI-M/MPI-ESM-LR/historical/day/atmos/day/r2i1p1/v20111006/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MPI-M/MPI-ESM-MR/historical/day/atmos/day/r2i1p1/v20120503/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MPI-M/MPI-ESM-P/historical/day/atmos/day/r2i1p1/v20120315/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/MRI/MRI-CGCM3/historical/day/atmos/day/r2i1p1/v20120701/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/NCC/NorESM1-M/historical/day/atmos/day/r2i1p1/v20110901/tasmin/
    /g/data1b/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-CM3/historical/day/atmos/day/r2i1p1/v20120227/tasmin/
    
    The following datasets are not yet available in the database, but they have been requested or recently downloaded
    cmip5.output1.LASG-IAP.FGOALS-s2.historical.day.atmos.day.r2i1p1.v20161204 tasmin status: queued 
    
    Available on ESGF but not locally:


The tool first search on the ESGF for all the files that match the
constraints we passed. It then looks for these file locally and if it
finds them it returns their path on raijin. For all the files it can’t
find locally, the tool check an NCI table listing the downloads they are
working on. Finally it lists missing datasets which are in the download
queue, followed by the datasets that are not available locally and no
one has yet requested.

The tool list the datasets paths and dataset_ids, if you want you can
get a more detailed list by file by passing the *–format file* option.

The query by default returns the latest available version. What if we
want to have a look at all the available versions?

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table Amon -m ACCESS1.0 --all-versions --format file


.. parsed-literal::

    None
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/files/tasmin_20120115/tasmin_Amon_ACCESS1-0_historical_r1i1p1_185001-200512.nc
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r2i1p1/files/tasmin_20130726/tasmin_Amon_ACCESS1-0_historical_r2i1p1_185001-200512.nc
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r3i1p1/files/tasmin_20140402/tasmin_Amon_ACCESS1-0_historical_r3i1p1_185001-200512.nc
    
    Everything available on ESGF is also available locally


The option *–all-versions* is the reverse of *–latest*, which is also
the default, so we get a list of all available versions. Since all the
ACCESS1.0 data is available on NCI (which is the authoritative source
for the ACCESS models) the tool shouldn’t find any missing datasets, if
it does please let us know about it.

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
      --realm [atmos|ocean|land|landIce|seaIce|aerosol|atmosChem|ocnBgchem]
      -se, --sub_experiment_id TEXT   Only available for hindcast and forecast
                                      experiments: sYYYY
      -vl, --variant_label TEXT       Indicates a model variant: r#i#p#f#
      --and [variable_id|experiment_id|table_id|realm|frequency|member_id|source_id|source_type|activity_id|grib_label|nominal_resolution|sub_experiment_id]
                                      Attributes for which we want to add AND
                                      filter, i.e. `--and variable_id` to apply to
                                      variable values
      --institution TEXT              Modelling group institution id: IPSL, NOAA-
                                      GFDL ...
      --cf_standard_name TEXT         CF variable standard_name, use instead of
                                      variable constraint
      --format [file|dataset]         Return output for datasets (default) or
                                      individual files
      --latest / --all-versions       Return only the latest version or all of
                                      them. Default: --latest
      --replica / --no-replica        Return both original files and replicas.
                                      Default: --no-replica
      --distrib / --no-distrib        Distribute search across all ESGF nodes.
                                      Default: --distrib
      --csv / --no-csv                Send output to csv file including extra
                                      information. Default: --no-csv
      --stats / --no-stats            Write summary of query results, works only
                                      with --local option. Default: --no-stats
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

    /g/data1b/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/1pctCO2/r1i1p1f2/Amon/tasmax/gr/v20180626
    /g/data1b/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-ESM2-1/1pctCO2/r1i1p1f2/Amon/tasmax/gr/v20181018
    /g/data1b/oi10/replicas/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-Veg/1pctCO2/r1i1p1f1/Amon/tasmax/gr/v20190702
    /g/data1b/oi10/replicas/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/1pctCO2/r1i1p1f1/Amon/tasmax/gr/v20180727
    /g/data1b/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/1pctCO2/r1i1p1f2/Amon/tasmin/gr/v20180626
    /g/data1b/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-ESM2-1/1pctCO2/r1i1p1f2/Amon/tasmin/gr/v20181018
    /g/data1b/oi10/replicas/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-Veg/1pctCO2/r1i1p1f1/Amon/tasmin/gr/v20190702
    /g/data1b/oi10/replicas/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/1pctCO2/r1i1p1f1/Amon/tasmin/gr/v20180727


In this example we used the *–local* option for the main command
**clef** to get only the local matching data path as output. Note also
that: - we are using abbreviations for the options where available; - we
are passing the variable *-v* option twice; - we used the CMIP6 specific
option *-g/–grid* to search for all data that is not on the model native
grid. This doesn’t indicate a grid common to all the CMIP6 output only
to the model itself, the same is true for member_id and other
attributes.

*–local* is actually executing the query directly on the NCI clef.nci.org.au 
database, which is different from the default query where the search is
executed first on the ESGF and then its results are matched locally. In
the example above the final result is exactly the same, whichever way we
perform the query. This way of searching can give you more results if a
node is offline or if a version have been unpublished from the ESGF but
is still available locally.

.. code:: ipython3

    !clef --missing cmip6 -e 1pctCO2 -v clw -v clwvi -t Amon -g gr


.. parsed-literal::

    None
    
    Available on ESGF but not locally:
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clw.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clwvi.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clw.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clwvi.gr.v20191020
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20180626
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20180626
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20181018
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20181018
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clw.gr.v20181031
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clwvi.gr.v20181031
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clw.gr.v20181107
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clwvi.gr.v20181107
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clw.gr.v20190328
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clwvi.gr.v20190328
    CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clw.gr.v20190718
    CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190718
    CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190702
    CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clw.gr.v20180727
    CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20180727


This time we used the *–missing* option and the tool returned only the
results matching the constraints that are available on the ESGF but not
locally (we changed variables to make sure to get some missing data
back).

.. code:: ipython3

    !clef --remote cmip6 -e 1pctCO2 -v tasmin -t Amon -g gr


.. parsed-literal::

    None
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.tasmin.gr.v20180626
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.tasmin.gr.v20181018
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.tasmin.gr.v20181031
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.tasmin.gr.v20181107
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.tasmin.gr.v20190328
    CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.1pctCO2.r1i1p1f1.Amon.tasmin.gr.v20190702
    CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.tasmin.gr.v20180727


The *–remote* option returns the Dataset_ids of the data matching the
constraints, regardless that they are available locally or not.

.. code:: ipython3

    !clef --remote cmip6 -e 1pctCO2 -v tasmin -t Amon -g gr -mi r1i1p1f2 --format file


.. parsed-literal::

    None
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.tasmin.gr.v20180626.tasmin_Amon_CNRM-CM6-1_1pctCO2_r1i1p1f2_gr_185001-199912.nc
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.tasmin.gr.v20181018.tasmin_Amon_CNRM-ESM2-1_1pctCO2_r1i1p1f2_gr_185001-199912.nc


Running the same command with the option *–format file* after the
sub-command, will return the File_ids instead of the default
Dataset_ids. Please note that *–local*, *–remote* and *–missing*
together with *–request*, which we will look at next, are all options of
the main command **clef** and they need to come before any sub-commands.

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

    None
    
    Available on ESGF but not locally:
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clw.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clwvi.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clw.gr.v20191020
    CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clwvi.gr.v20191020
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20180626
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20180626
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20181018
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20181018
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clw.gr.v20181031
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clwvi.gr.v20181031
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clw.gr.v20181107
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clwvi.gr.v20181107
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clw.gr.v20190328
    CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clwvi.gr.v20190328
    CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clw.gr.v20190718
    CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190718
    CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190702
    CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clw.gr.v20180727
    CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20180727
    
    Finished writing file: CMIP6_pxp581_20191114T134444.txt
    Do you want to proceed with request for missing files? (N/Y)
     No is default
    Your request has been saved in 
     /home/581/pxp581/clef/docs/CMIP6_pxp581_20191114T134444.txt
    You can use this file to request the data via the NCI helpdesk: help@nci.org.au  or https://help.nci.org.au.


We run the same query which gave us as a result 4 missing datasets but
this time we used the *–request* option after **clef**. The tool will
execute the query remotely, then look for matches locally and on the NCI
download list. Having found none gives as an option of putting in a
request. It will accept any of the following as a positive answer: > Y
YES y yes

With anything else or if you don’t pass anything it will assume you
don’t want to put in a request. It still saved the request in a file we
can use later.

.. code:: ipython3

    !cat CMIP6_*.txt


.. parsed-literal::

    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clw.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clw.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20180626
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20180626
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20181018
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20181018
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clw.gr.v20181031
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clwvi.gr.v20181031
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clw.gr.v20181107
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clwvi.gr.v20181107
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clw.gr.v20190328
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clwvi.gr.v20190328
    dataset_id=CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clw.gr.v20190718
    dataset_id=CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190718
    dataset_id=CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190702
    dataset_id=CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clw.gr.v20180727
    dataset_id=CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20180727
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clw.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clw.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20180626
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20180626
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20181018
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20181018
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clw.gr.v20181031
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clwvi.gr.v20181031
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clw.gr.v20181107
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clwvi.gr.v20181107
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clw.gr.v20190328
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clwvi.gr.v20190328
    dataset_id=CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clw.gr.v20190718
    dataset_id=CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190718
    dataset_id=CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190702
    dataset_id=CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clw.gr.v20180727
    dataset_id=CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20180727
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clw.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r2i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clw.gr.v20191020
    dataset_id=CMIP6.CMIP.CAS.FGOALS-f3-L.1pctCO2.r3i1p1f1.Amon.clwvi.gr.v20191020
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20180626
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20180626
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clw.gr.v20181018
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r1i1p1f2.Amon.clwvi.gr.v20181018
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clw.gr.v20181031
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r2i1p1f2.Amon.clwvi.gr.v20181031
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clw.gr.v20181107
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r3i1p1f2.Amon.clwvi.gr.v20181107
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clw.gr.v20190328
    dataset_id=CMIP6.CMIP.CNRM-CERFACS.CNRM-ESM2-1.1pctCO2.r4i1p1f2.Amon.clwvi.gr.v20190328
    dataset_id=CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clw.gr.v20190718
    dataset_id=CMIP6.CMIP.E3SM-Project.E3SM-1-0.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190718
    dataset_id=CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3-Veg.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20190702
    dataset_id=CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clw.gr.v20180727
    dataset_id=CMIP6.CMIP.IPSL.IPSL-CM6A-LR.1pctCO2.r1i1p1f1.Amon.clwvi.gr.v20180727


If I answered ‘yes’ the tool would have sent an e-mail to the NCI
helpdesk with the text file attached, NCI can pass that file as input to
their download tool and queue your request. NB if you are running clef
from raijin you cannot send an e-mail so in that case the tool will
remind you you you need to send an e-mail to the NCI helpdesk yourself
to finalise the request.

Integrating the local query in your scripts
-------------------------------------------

Until now we looked at how to run queries from the command line, but you
can use use the same query run by the *–local* option directly in your
python code. By doing so you also get access to a lot more information
on the datasets returned not only the path. To do so we have first to
import some functions from the clef.code sub-module. In particular the
**search()** function and **connect()** and **Session()** that we’ll use
to open a connection to the database.

.. code:: ipython3

    from clef.code import *
    db = connect()
    s = Session()

Running search()
~~~~~~~~~~~~~~~~

**search()** takes 4 inputs: the db session, the project (i.e. currently
‘cmip5’ or ‘cmip6’), latest (True or False) and a dictionary containing
the query constraints: > search(session, project=‘CMIP5’, latest=True,
\**kwargs)

Let’s start by defining some constraints.

.. code:: ipython3

    constraints = {'variable': 'tas', 'model': 'MIROC5', 'cmor_table': 'day', 'experiment': 'rcp85'}

The available keys depend on the project you are querying and the
attributes stored by the database. You can use any of the *facets* used
for ESGF but in future we will be adding other options based on extra
fields which are stored as attributes.

.. code:: ipython3

    results = search(s, project='CMIP5', **constraints)
    results




.. parsed-literal::

    [{'filenames': ['tas_day_MIROC5_rcp85_r1i1p1_20100101-20191231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20300101-20391231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20400101-20491231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20500101-20591231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20800101-20891231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_21000101-21001231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20060101-20091231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20600101-20691231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20700101-20791231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20200101-20291231.nc'],
      'project': 'CMIP5',
      'institute': 'MIROC',
      'model': 'MIROC5',
      'experiment': 'rcp85',
      'frequency': 'day',
      'realm': 'atmos',
      'r': '1',
      'i': '1',
      'p': '1',
      'ensemble': 'r1i1p1',
      'cmor_table': 'day',
      'version': '20120710',
      'variable': 'tas',
      'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas',
      'periods': [('20100101', '20191231'),
       ('20900101', '20991231'),
       ('20300101', '20391231'),
       ('20400101', '20491231'),
       ('20500101', '20591231'),
       ('20800101', '20891231'),
       ('21000101', '21001231'),
       ('20060101', '20091231'),
       ('20600101', '20691231'),
       ('20700101', '20791231'),
       ('20200101', '20291231')],
      'fdate': '20060101',
      'tdate': '21001231',
      'time_complete': True},
     {'filenames': ['tas_day_MIROC5_rcp85_r2i1p1_20900101-20991231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20500101-20591231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20800101-20891231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20700101-20791231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20400101-20491231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20200101-20291231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20100101-20191231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_21000101-21001231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20300101-20391231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20600101-20691231.nc',
       'tas_day_MIROC5_rcp85_r2i1p1_20060101-20091231.nc'],
      'project': 'CMIP5',
      'institute': 'MIROC',
      'model': 'MIROC5',
      'experiment': 'rcp85',
      'frequency': 'day',
      'realm': 'atmos',
      'r': '2',
      'i': '1',
      'p': '1',
      'ensemble': 'r2i1p1',
      'cmor_table': 'day',
      'version': '20120710',
      'variable': 'tas',
      'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r2i1p1/v20120710/tas',
      'periods': [('20900101', '20991231'),
       ('20500101', '20591231'),
       ('20800101', '20891231'),
       ('20700101', '20791231'),
       ('20400101', '20491231'),
       ('20200101', '20291231'),
       ('20100101', '20191231'),
       ('21000101', '21001231'),
       ('20300101', '20391231'),
       ('20600101', '20691231'),
       ('20060101', '20091231')],
      'fdate': '20060101',
      'tdate': '21001231',
      'time_complete': True},
     {'filenames': ['tas_day_MIROC5_rcp85_r3i1p1_20700101-20791231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20800101-20891231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20200101-20291231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20600101-20691231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20500101-20591231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20300101-20391231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20900101-20991231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20060101-20091231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20100101-20191231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_20400101-20491231.nc',
       'tas_day_MIROC5_rcp85_r3i1p1_21000101-21001231.nc'],
      'project': 'CMIP5',
      'institute': 'MIROC',
      'model': 'MIROC5',
      'experiment': 'rcp85',
      'frequency': 'day',
      'realm': 'atmos',
      'r': '3',
      'i': '1',
      'p': '1',
      'ensemble': 'r3i1p1',
      'cmor_table': 'day',
      'version': '20120710',
      'variable': 'tas',
      'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r3i1p1/v20120710/tas',
      'periods': [('20700101', '20791231'),
       ('20800101', '20891231'),
       ('20200101', '20291231'),
       ('20600101', '20691231'),
       ('20500101', '20591231'),
       ('20300101', '20391231'),
       ('20900101', '20991231'),
       ('20060101', '20091231'),
       ('20100101', '20191231'),
       ('20400101', '20491231'),
       ('21000101', '21001231')],
      'fdate': '20060101',
      'tdate': '21001231',
      'time_complete': True},
     {'filenames': ['tas_day_MIROC5_rcp85_r4i1p1_20200101-20291231.nc',
       'tas_day_MIROC5_rcp85_r4i1p1_20100101-20191231.nc',
       'tas_day_MIROC5_rcp85_r4i1p1_20060101-20091231.nc',
       'tas_day_MIROC5_rcp85_r4i1p1_20300101-20351231.nc'],
      'project': 'CMIP5',
      'institute': 'MIROC',
      'model': 'MIROC5',
      'experiment': 'rcp85',
      'frequency': 'day',
      'realm': 'atmos',
      'r': '4',
      'i': '1',
      'p': '1',
      'ensemble': 'r4i1p1',
      'cmor_table': 'day',
      'version': '20131009',
      'variable': 'tas',
      'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r4i1p1/v20131009/tas',
      'periods': [('20200101', '20291231'),
       ('20100101', '20191231'),
       ('20060101', '20091231'),
       ('20300101', '20351231')],
      'fdate': '20060101',
      'tdate': '20351231',
      'time_complete': True},
     {'filenames': ['tas_day_MIROC5_rcp85_r5i1p1_20060101-20091231.nc',
       'tas_day_MIROC5_rcp85_r5i1p1_20100101-20191231.nc',
       'tas_day_MIROC5_rcp85_r5i1p1_20300101-20351231.nc',
       'tas_day_MIROC5_rcp85_r5i1p1_20200101-20291231.nc'],
      'project': 'CMIP5',
      'institute': 'MIROC',
      'model': 'MIROC5',
      'experiment': 'rcp85',
      'frequency': 'day',
      'realm': 'atmos',
      'r': '5',
      'i': '1',
      'p': '1',
      'ensemble': 'r5i1p1',
      'cmor_table': 'day',
      'version': '20131009',
      'variable': 'tas',
      'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r5i1p1/v20131009/tas',
      'periods': [('20060101', '20091231'),
       ('20100101', '20191231'),
       ('20300101', '20351231'),
       ('20200101', '20291231')],
      'fdate': '20060101',
      'tdate': '20351231',
      'time_complete': True}]



Both the keys and values of the constraints get checked before being
passed to the query function. This means that if you passed a key or a
value that doesn’t exist for the chosen project, the function will print
a list of valid values and then exit. Let’s re-write the constraints
dictionary to show an example.

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'activity': 'CMIP'}
    results = search(s, **constraints)


::


    ---------------------------------------------------------------------------

    ClefException                             Traceback (most recent call last)

    <ipython-input-18-c5717342465f> in <module>
          1 constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'activity': 'CMIP'}
    ----> 2 results = search(s, **constraints)
    

    ~/.local/lib/python3.6/site-packages/clef/code.py in search(session, project, latest, **kwargs)
         38     project=project.upper()
         39     valid_keys = get_keys(project)
    ---> 40     args = check_keys(valid_keys, kwargs)
         41     vocabularies = load_vocabularies(project)
         42     check_values(vocabularies, project, args)


    ~/.local/lib/python3.6/site-packages/clef/code.py in check_keys(valid_keys, kwargs)
        233         if facet==[]:
        234             raise ClefException(
    --> 235                 f"Warning {key} is not a valid constraint name"
        236                 f"Valid constraints are:\n{valid_keys.values()}")
        237         else:


    ClefException: Warning activity is not a valid constraint nameValid constraints are:
    dict_values([['source_id', 'model', 'm'], ['realm'], ['time_frequency', 'frequency', 'f'], ['variable_id', 'variable', 'v'], ['experiment_id', 'experiment', 'e'], ['table_id', 'table', 'cmor_table', 't'], ['member_id', 'member', 'ensemble', 'en', 'mi'], ['institution_id', 'institution', 'institute'], ['experiment_family']])


You can see that the function told us ‘activity’ is not a valid
constraints for CMIP5, in fact that can be used only with CMIP6 NB. that
the search accepted all the other abbreviations, there’s a few terms
that can be used for each key. The full list of valid keys is available
from from the github repository:
https://github.com/coecms/clef/blob/master/clef/data/valid_keys.json

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'member': 'r1i1p1'}
    results = search(s, **constraints)
    results[0]




.. parsed-literal::

    {'filenames': ['tas_day_MIROC5_rcp85_r1i1p1_20100101-20191231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20300101-20391231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20400101-20491231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20500101-20591231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20800101-20891231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_21000101-21001231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20060101-20091231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20600101-20691231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20700101-20791231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20200101-20291231.nc'],
     'project': 'CMIP5',
     'institute': 'MIROC',
     'model': 'MIROC5',
     'experiment': 'rcp85',
     'frequency': 'day',
     'realm': 'atmos',
     'r': '1',
     'i': '1',
     'p': '1',
     'ensemble': 'r1i1p1',
     'cmor_table': 'day',
     'version': '20120710',
     'variable': 'tas',
     'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas',
     'periods': [('20100101', '20191231'),
      ('20900101', '20991231'),
      ('20300101', '20391231'),
      ('20400101', '20491231'),
      ('20500101', '20591231'),
      ('20800101', '20891231'),
      ('21000101', '21001231'),
      ('20060101', '20091231'),
      ('20600101', '20691231'),
      ('20700101', '20791231'),
      ('20200101', '20291231')],
     'fdate': '20060101',
     'tdate': '21001231',
     'time_complete': True}



NB that *project* is by default ‘CMIP5’ so it can be omitted when
querying CMIP5 data and *latest* is True by default. Set this to *False*
if you want to return all the available versions.

Running search() for different sets of attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The **search()** function works for one set of attributes, you can
specify only one value for each of the attributes at one time. If you
want to run a query for two or more different sets of attributes you can
call **search()** in a loop. If you have a small numbers of queries then
this is easy to implement and run. To make **search()** works for a
random number of inputs passed by the command line we set up a function
**call_local_query()** that deals with this more efficiently. The
arguments are very similar to **search()** with the important difference
that we are passing list of values instead of strings:
>call_local_query(s, project, oformat, latest, \**kwargs)

Let’s look at an example:

.. code:: ipython3

    constraints = {'variable': ['tasmin','tasmax'], 'model': ['MIROC5','MIROC4h'],
                   'cmor_table': ['day'], 'experiment': ['rcp85'], 'ensemble': ['r1i1p1']}
    results, paths = call_local_query(s, project='CMIP5', oformat='Dataset', latest=True, **constraints)

Because this function was created to deliver results for the command
line local query option, as well as the list of results, it also outputs
a list of their paths. Under the hood this function works out all the
combinations of the arguments you passed and will run **search()** for
each of them, before doing so will also run other functions that check
that the values and keys passed to the function are valid. The extra
arguments *oformat* and “latest” are necessary to resolve the command
line *–format* and *–latest* option respectively. The first can be
‘file’ or ‘dataset’, with the last being the default. It influences the
*paths* output but no *results* which will contain all the datasets
information including filenames.

AND Filter
~~~~~~~~~~

We started adding additional features to CleF which allows more complex
queries. We started from the following case. Let’s say that you want to
find all the CMIP6 models that have both daily precipitation (pr) and
soil moisture (mrso) for a particular experiment(historical). Up to now
you would had to select separately both variables and then work out
which models had both on your own.

We will show how this work starting by using the actual function
interactively. There is also a command line option but it returns only a
list of the models. First of all, since we are potentially passing more
than one value to the query we are using lists in our *constraints*
dictionary. Then we need to define the attributes for which we want all
values to be present, only *variable_id* in this case. Finally we tell
the function which attributes define a simulation, this would most often
be *model* and *member*.

.. code:: ipython3

    constraints = {'variable_id': ['pr','mrso'], 'frequency': ['mon'], 'experiment_id': ['historical']}
    allvalues = ['variable_id']
    fixed = ['source_id', 'member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)

The function returns the selected models/members combinations that have
both variables and the corresponding subset of the original query
*results*. NB currently using the abbreviated version for the
constraints keys won’t work, you will have to use the attributes full
names. You can see by printing the length of both lists and one of the
first item of *selection* that the results have been grouped by
models/ensembles and then filtered.

.. code:: ipython3

    print(len(results),len(selection))
    selection[0]


.. parsed-literal::

    46 23




.. parsed-literal::

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'comb': {('mrso',), ('pr',)},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114'},
     'version': {'v20181114', 'v20181126'}}



The full definition the **matching()** shows all the function arguments:
>matching(session, cols, fixed, project=‘CMIP5’, local=True,
latest=True, \**kwargs)

From this you can see that like **search()** by default *project* is
‘CMIP5’ and *latest* is True. We didn’t have to use yet the *local*
argument which is True by default, we will see examples later where is
set to False so we can do the same query remotely.

AND filter on more than one attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can pass more than value for more than one attribute, let’s add
*piControl* to the experiment list.

.. code:: ipython3

    constraints = {'variable_id': ['pr','mrso'], 'frequency': ['mon'], 'experiment_id': ['historical', 'piControl']}
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]


.. parsed-literal::

    100 29




.. parsed-literal::

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'comb': {('mrso',), ('pr',)},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Amon/pr/gn/v20181016',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Lmon/mrso/gn/v20181012'},
     'version': {'v20181012', 'v20181016', 'v20181114', 'v20181126'}}



As you can see we get now many more results but only a few more
combinations after applying the filter. This is because we are still
defining a simulation by using model and member combinations we haven’t
included experiment and the results for the two experiments are grouped
together, to fix this we need to add *experiment_id* to the *fixed*
list.

.. code:: ipython3

    fixed = ['source_id', 'member_id','experiment_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]


.. parsed-literal::

    98 49




.. parsed-literal::

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'experiment_id': 'historical',
     'comb': {('mrso',), ('pr',)},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114'},
     'version': {'v20181114', 'v20181126'}}



If we wanted to find all models/members combinations which have both
variables and both experiments, then we should have kept *fixed* as it
was and add *experiment_id* to the *allvalues* list instead.

.. code:: ipython3

    allvalues = ['variable_id', 'experiment_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]


.. parsed-literal::

    80 20




.. parsed-literal::

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'comb': {('mrso', 'historical'),
      ('mrso', 'piControl'),
      ('pr', 'historical'),
      ('pr', 'piControl')},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Amon/pr/gn/v20181016',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Lmon/mrso/gn/v20181012'},
     'version': {'v20181012', 'v20181016', 'v20181114', 'v20181126'}}



AND filter applied to remote ESGF query
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can of course do the same query for CMIP5, in that case you can omit
*project* when calling the function since its default value is ‘CMIP5’.
Another default option is *local=True*, this says the function to perfom
this query directly on local database if you want you can perform the same query on
the ESGF database, so you can see what has been published.

.. code:: ipython3

    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['Amon'], 'experiment': ['historical','rcp26', 'rcp85']}
    allvalues = ['variable', 'experiment']
    fixed=['model','ensemble']
    results, selection = matching(s, allvalues, fixed, local=False, **constraints)
    print(len(results),len(selection))
    selection[0]


.. parsed-literal::

    None
    1488 46




.. parsed-literal::

    {'model': 'CNRM-CM5',
     'ensemble': 'r1i1p1',
     'comb': {('tasmax', 'historical'),
      ('tasmax', 'rcp26'),
      ('tasmax', 'rcp85'),
      ('tasmin', 'historical'),
      ('tasmin', 'rcp26'),
      ('tasmin', 'rcp85')},
     'cmor_table': {'Amon'},
     'dataset_id': {'cmip5.output1.CNRM-CERFACS.CNRM-CM5.historical.mon.atmos.Amon.r1i1p1.v20110901|esg1.umr-cnrm.fr',
      'cmip5.output1.CNRM-CERFACS.CNRM-CM5.rcp26.mon.atmos.Amon.r1i1p1.v20110629|esg1.umr-cnrm.fr',
      'cmip5.output1.CNRM-CERFACS.CNRM-CM5.rcp85.mon.atmos.Amon.r1i1p1.v20110930|esg1.umr-cnrm.fr'},
     'version': {'v20110629', 'v20110901', 'v20110930'}}



Please note how I used different attributes names because we are
querying CMIP5 now. *comb* highlights all the combinations that have to
be present for a model/ensemble to be returned while we are getting a
dataset_id rather than a directory path.

AND filter on the command line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command line version of **matching** can be called using the *–and*
flag followed by the attribute for which we want all values, the flag
can be used more than once. By default model/ensemble combinations
define a simulation, and only model, ensemble and version are returned
as final result.

.. code:: ipython3

    !clef --local cmip5 -v tasmin -v tasmax -e rcp26 -e rcp85 -e historical -t Amon --and variable


.. parsed-literal::

    ACCESS1.0 r1i1p1 {None}
    ACCESS1.0 r2i1p1 {None}
    ACCESS1.0 r3i1p1 {None}
    ACCESS1.3 r1i1p1 {None}
    ACCESS1.3 r2i1p1 {None}
    ACCESS1.3 r3i1p1 {None}
    BCC-CSM1.1 r1i1p1 {'1', '20120705'}
    BCC-CSM1.1 r2i1p1 {'1'}
    BCC-CSM1.1 r3i1p1 {'1'}
    BCC-CSM1.1(m) r1i1p1 {'20120709', '20130405', '20120910'}
    BCC-CSM1.1(m) r2i1p1 {'20120709'}
    BCC-CSM1.1(m) r3i1p1 {'20120709'}
    BNU-ESM r1i1p1 {'20120510'}
    CCSM4 r1i1p1 {'20130426', '20160829'}
    CCSM4 r1i2p1 {'20130715'}
    CCSM4 r1i2p2 {'20130715'}
    CCSM4 r2i1p1 {'20121031', '20160829'}
    CCSM4 r3i1p1 {'20121031', '20160829'}
    CCSM4 r4i1p1 {'20121031', '20160829'}
    CCSM4 r5i1p1 {'20121031', '20160829'}
    CCSM4 r6i1p1 {'20120709', '20160829'}
    CESM1(BGC) r1i1p1 {'20130213', '20130216'}
    CESM1(CAM5) r1i1p1 {'20130313'}
    CESM1(CAM5) r2i1p1 {'20130313'}
    CESM1(CAM5) r3i1p1 {'20130313', '20140310'}
    CESM1(WACCM) r1i1p1 {'20130314'}
    CESM1(WACCM) r2i1p1 {'20130314'}
    CESM1(WACCM) r3i1p1 {'20130314', '20130315'}
    CESM1(WACCM) r4i1p1 {'20130314', '20130315'}
    CESM1-FASTCHEM r1i1p1 {'20121029'}
    CESM1-FASTCHEM r2i1p1 {'20121029'}
    CESM1-FASTCHEM r3i1p1 {'20121029'}
    CMCC-CESM r1i1p1 {'20170725'}
    CMCC-CM r1i1p1 {'20170725'}
    CMCC-CMS r1i1p1 {'20170725'}
    CNRM-CM5 r10i1p1 {'20110915', '20110901'}
    CNRM-CM5 r1i1p1 {'20110629', '20110930', '20110901'}
    CNRM-CM5 r2i1p1 {'20110915', '20110901'}
    CNRM-CM5 r3i1p1 {'20110901'}
    CNRM-CM5 r4i1p1 {'20110915', '20110901'}
    CNRM-CM5 r5i1p1 {'20110901'}
    CNRM-CM5 r6i1p1 {'20110915', '20110901'}
    CNRM-CM5 r7i1p1 {'20110901'}
    CNRM-CM5 r8i1p1 {'20110901'}
    CNRM-CM5 r9i1p1 {'20110901'}
    CNRM-CM5-2 r1i1p1 {'20130401'}
    CSIRO-Mk3.6.0 r10i1p1 {None}
    CSIRO-Mk3.6.0 r1i1p1 {None}
    CSIRO-Mk3.6.0 r2i1p1 {None}
    CSIRO-Mk3.6.0 r3i1p1 {None}
    CSIRO-Mk3.6.0 r4i1p1 {None}
    CSIRO-Mk3.6.0 r5i1p1 {None}
    CSIRO-Mk3.6.0 r6i1p1 {None}
    CSIRO-Mk3.6.0 r7i1p1 {None}
    CSIRO-Mk3.6.0 r8i1p1 {None}
    CSIRO-Mk3.6.0 r9i1p1 {None}
    CSIRO-Mk3L-1-2 r1i1p1 {None}
    CSIRO-Mk3L-1-2 r1i2p1 {None}
    CSIRO-Mk3L-1-2 r2i2p1 {None}
    CSIRO-Mk3L-1-2 r3i2p1 {None}
    CanESM2 r1i1p1 {'20120718'}
    CanESM2 r2i1p1 {'20120718'}
    CanESM2 r3i1p1 {'20120718'}
    CanESM2 r4i1p1 {'20120718'}
    CanESM2 r5i1p1 {'20120718'}
    EC-EARTH r11i1p1 {'20171115'}
    EC-EARTH r12i1p1 {'20131231'}
    EC-EARTH r14i1p1 {'20121115'}
    EC-EARTH r6i1p1 {'20130315'}
    EC-EARTH r8i1p1 {'20171115'}
    FGOALS-s2 r2i1p1 {'1'}
    FGOALS-s2 r3i1p1 {'1'}
    FGOALS_g2 r1i1p1 {'20161204', '1'}
    FGOALS_g2 r2i1p1 {'20161204'}
    FGOALS_g2 r3i1p1 {'20161204'}
    FGOALS_g2 r4i1p1 {'20161204'}
    FGOALS_g2 r5i1p1 {'20161204'}
    FIO-ESM r1i1p1 {'20120524', '20120522', '20121010'}
    FIO-ESM r2i1p1 {'20120524', '20120522'}
    FIO-ESM r3i1p1 {'20120524', '20120522'}
    GFDL-CM3 r1i1p1 {'20120227'}
    GFDL-CM3 r2i1p1 {'20120227'}
    GFDL-CM3 r3i1p1 {'20120227'}
    GFDL-CM3 r4i1p1 {'20120227'}
    GFDL-CM3 r5i1p1 {'20120227'}
    GFDL-ESM2G r1i1p1 {'20120412'}
    GFDL-ESM2M r1i1p1 {'20111228'}
    GISS-E2-H r1i1p1 {'20160426', '20160512'}
    GISS-E2-H r1i1p2 {'20160426', '20160512'}
    GISS-E2-H r1i1p3 {'20160426', '20160512'}
    GISS-E2-H r2i1p1 {'20160426', '20160512'}
    GISS-E2-H r2i1p2 {'20160426'}
    GISS-E2-H r2i1p3 {'20160426', '20160512'}
    GISS-E2-H r3i1p1 {'20160426'}
    GISS-E2-H r3i1p2 {'20160426'}
    GISS-E2-H r3i1p3 {'20160426'}
    GISS-E2-H r4i1p1 {'20160426'}
    GISS-E2-H r4i1p2 {'20160426'}
    GISS-E2-H r4i1p3 {'20160426'}
    GISS-E2-H r5i1p1 {'20160426'}
    GISS-E2-H r5i1p2 {'20160426'}
    GISS-E2-H r5i1p3 {'20160426'}
    GISS-E2-H r6i1p1 {'20160426'}
    GISS-E2-H r6i1p3 {'20160426'}
    GISS-E2-H-CC r1i1p1 {'20160426', '20160512'}
    GISS-E2-R r1i1p1 {'20160513', '20160502', '20160512'}
    GISS-E2-R r1i1p121 {'20160502'}
    GISS-E2-R r1i1p122 {'20160502'}
    GISS-E2-R r1i1p124 {'20160502'}
    GISS-E2-R r1i1p125 {'20160502'}
    GISS-E2-R r1i1p126 {'20160502'}
    GISS-E2-R r1i1p127 {'20160502'}
    GISS-E2-R r1i1p128 {'20160502'}
    GISS-E2-R r1i1p2 {'20160513', '20160502', '20160512'}
    GISS-E2-R r1i1p3 {'20160513', '20160512', '20160503'}
    GISS-E2-R r2i1p1 {'20160513', '20160503'}
    GISS-E2-R r2i1p2 {'20160503'}
    GISS-E2-R r2i1p3 {'20160513', '20160503'}
    GISS-E2-R r3i1p1 {'20160503'}
    GISS-E2-R r3i1p2 {'20160503'}
    GISS-E2-R r3i1p3 {'20160503'}
    GISS-E2-R r4i1p1 {'20160503'}
    GISS-E2-R r4i1p2 {'20160503'}
    GISS-E2-R r4i1p3 {'20160503'}
    GISS-E2-R r5i1p1 {'20160503'}
    GISS-E2-R r5i1p2 {'20160503'}
    GISS-E2-R r5i1p3 {'20160503'}
    GISS-E2-R r6i1p1 {'20160503'}
    GISS-E2-R r6i1p2 {'20160503'}
    GISS-E2-R r6i1p3 {'20160503'}
    GISS-E2-R-CC r1i1p1 {'20160502', '20160512'}
    HadCM3 r10i1p1 {'20110728'}
    HadCM3 r1i1p1 {'20110823'}
    HadCM3 r2i1p1 {'20110728'}
    HadCM3 r3i1p1 {'20110905'}
    HadCM3 r4i1p1 {'20110728'}
    HadCM3 r5i1p1 {'20110905'}
    HadCM3 r6i1p1 {'20110728'}
    HadCM3 r7i1p1 {'20110728'}
    HadCM3 r8i1p1 {'20110905'}
    HadCM3 r9i1p1 {'20110728'}
    HadGEM2-AO r1i1p1 {'20130815'}
    HadGEM2-CC r1i1p1 {'20120531', '20110927'}
    HadGEM2-CC r2i1p1 {'20111129', '20111215'}
    HadGEM2-CC r3i1p1 {'20120105', '20111208'}
    HadGEM2-ES r1i1p1 {'20130430', '20111206', '20120928'}
    HadGEM2-ES r2i1p1 {'20111205', '20110418', '20120114'}
    HadGEM2-ES r3i1p1 {'20110418', '20111208', '20120114'}
    HadGEM2-ES r4i1p1 {'20110418', '20111209', '20120114'}
    HadGEM2-ES r5i1p1 {'20130312'}
    IPSL-CM5A-LR r1i1p1 {'20110406', '20111103', '20120114'}
    IPSL-CM5A-LR r2i1p1 {'20110726', '20110406', '20120114'}
    IPSL-CM5A-LR r3i1p1 {'20111119', '20110726', '20110406'}
    IPSL-CM5A-LR r4i1p1 {'20120804', '20110726', '20130506'}
    IPSL-CM5A-LR r5i1p1 {'20111119'}
    IPSL-CM5A-LR r6i1p1 {'20120526'}
    IPSL-CM5A-MR r1i1p1 {'20111119'}
    IPSL-CM5A-MR r2i1p1 {'20120430'}
    IPSL-CM5A-MR r3i1p1 {'20130506'}
    IPSL-CM5B-LR r1i1p1 {'20120430', '20120114'}
    MIROC-ESM r1i1p1 {'20120710'}
    MIROC-ESM r2i1p1 {'20120710'}
    MIROC-ESM r3i1p1 {'20120710'}
    MIROC-ESM-CHEM r1i1p1 {'20120710'}
    MIROC4h r1i1p1 {'20120628'}
    MIROC4h r2i1p1 {'20120628'}
    MIROC4h r3i1p1 {'20120628'}
    MIROC5 r1i1p1 {'20161012', '20120710'}
    MIROC5 r2i1p1 {'20120710'}
    MIROC5 r3i1p1 {'20120710'}
    MIROC5 r4i1p1 {'20131009', '20121221'}
    MIROC5 r5i1p1 {'20131009', '20120710'}
    MPI-ESM-LR r1i1p1 {'20120315'}
    MPI-ESM-LR r2i1p1 {'20120315'}
    MPI-ESM-LR r3i1p1 {'20120315'}
    MPI-ESM-MR r1i1p1 {'20120503'}
    MPI-ESM-MR r2i1p1 {'20120503'}
    MPI-ESM-MR r3i1p1 {'20120503'}
    MPI-ESM-P r1i1p1 {'20120315'}
    MPI-ESM-P r2i1p1 {'20120315'}
    MRI-CGCM3 r1i1p1 {'20120701'}
    MRI-CGCM3 r2i1p1 {'20120701'}
    MRI-CGCM3 r3i1p1 {'20120701'}
    MRI-CGCM3 r4i1p2 {'20120701'}
    MRI-CGCM3 r5i1p2 {'20120701'}
    MRI-ESM1 r1i1p1 {'20130307', '20140210'}
    NorESM1-M r1i1p1 {'20110912', '20110901'}
    NorESM1-M r2i1p1 {'20110901'}
    NorESM1-M r3i1p1 {'20110901'}
    inmcm4 r1i1p1 {'20130207'}


The same will work for *–remote* and *cmip6*

.. code:: ipython3

    !clef --remote cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id


.. parsed-literal::

    None
    BCC-CSM2-MR r1i1p1f1 {'v20181016', 'v20181012'}
    BCC-ESM1 r1i1p1f1 {'v20181211', 'v20181214'}
    CAMS-CSM1-0 r1i1p1f1 {'v20190729'}
    CESM2 r1i1p1f1 {'v20190320'}
    CESM2-WACCM r1i1p1f1 {'v20190320'}
    CanESM5 r1i1p1f1 {'v20190429'}
    E3SM-1-0 r1i1p1f1 {'v20190719', 'v20190807'}
    EC-Earth3 r1i1p1f1 {'v20190712'}
    EC-Earth3-Veg r1i1p1f1 {'v20190619'}
    GISS-E2-1-G r1i1p1f1 {'v20180824'}
    GISS-E2-1-G-CC r1i1p1f1 {'v20190815'}
    GISS-E2-1-H r1i1p1f1 {'v20190410'}
    HadGEM3-GC31-LL r1i1p1f1 {'v20190628'}
    HadGEM3-GC31-MM r1i1p1f1 {'v20190920'}
    IPSL-CM6A-LR r1i1p1f1 {'v20181123'}
    MCM-UA-1-0 r1i1p1f1 {'v20191017', 'v20190731'}
    MIROC6 r1i1p1f1 {'v20190311', 'v20181212'}
    MPI-ESM1-2-HR r1i1p1f1 {'v20190710'}
    MRI-ESM2-0 r1i1p1f1 {'v20190603', 'v20190222'}
    NorCPM1 r1i1p1f1 {'v20190914'}
    SAM0-UNICON r1i1p1f1 {'v20190910'}


New features
------------

We recently added new output features following a user request. These
are currently only available in the analysis3-unstable environment

.. code:: ipython3

    # !module load conda/analysis3-unstable

CSV file output
~~~~~~~~~~~~~~~

The *–csv* option added to the command line will output the query
results in a csv file. rather than getting only the files path, it will
list all the available attributes. This currently works only with the
*–local* option, it doesn’t yet work for the standard search or remote.
These last both perform an ESGF query rather than searching directly the
local database as *local* so they need to be treated differently. We are
still working on this.

.. code:: ipython3

    !clef --local cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id --csv


.. parsed-literal::

    BCC-CSM2-MR r1i1p1f1 {'v20181016', 'v20181012'}
    BCC-ESM1 r1i1p1f1 {'v20181211', 'v20181214'}
    CAMS-CSM1-0 r1i1p1f1 {'v20190729'}
    CESM2 r1i1p1f1 {'v20190320'}
    CESM2-WACCM r1i1p1f1 {'v20190320'}
    CanESM5 r1i1p1f1 {'v20190429'}
    EC-Earth3 r1i1p1f1 {'v20190712'}
    EC-Earth3-Veg r1i1p1f1 {'v20190619'}
    GISS-E2-1-G r1i1p1f1 {'v20180824'}
    GISS-E2-1-G-CC r1i1p1f1 {'v20190815'}
    GISS-E2-1-H r1i1p1f1 {'v20190410'}
    HadGEM3-GC31-LL r1i1p1f1 {'v20190628'}
    HadGEM3-GC31-MM r1i1p1f1 {'v20190920'}
    IPSL-CM6A-LR r1i1p1f1 {'v20181123'}
    MCM-UA-1-0 r1i1p1f1 {'v20190731', 'v20191017'}
    MIROC6 r1i1p1f1 {'v20181212', 'v20190311'}
    MPI-ESM1-2-HR r1i1p1f1 {'v20190710'}
    MRI-ESM2-0 r1i1p1f1 {'v20190603', 'v20190222'}
    NorCPM1 r1i1p1f1 {'v20190914'}
    NorESM2-LM r1i1p1f1 {'v20190815'}
    SAM0-UNICON r1i1p1f1 {'v20190910'}


.. code:: ipython3

    !head -n 4 CMIP6_query.csv


.. parsed-literal::

    
    
    
    


Query summary option
~~~~~~~~~~~~~~~~~~~~

The *–stats* option added to the command line will print a summary of
the query results It works for both *–local* and *–remote* options, but
not with the default query. Currently it prints the following: \* total
number of models, followed by their names \* total number of unique
model-ensembles/members combinations \* number of models that have N
ensembles/members, followed by their names

.. code:: ipython3

    !clef --local cmip5 -v pr -v mrso -e piControl --frequency mon --stats


.. parsed-literal::

    
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
start from the errata:

.. code:: ipython3

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
function. This first retrieve the message associted to any error_id and
then prints it in a human readable form, including the url for the
original error report. Let’s now have a look at how to retrieve and
print some documentation from ESDOC.

.. code:: ipython3

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
    overview > MIROC6 is a physical climate model mainly composed of three sub-models: atmosphere, land, and sea ice-ocean. The atmospheric model is based on the CCSR-NIES atmospheric general circulation model. The horizontal resolution is a T85 spectral truncation that is an approximately 1.4° grid interval for both latitude and longitude. The vertical grid coordinate is a hybrid σ-p coordinate. The model top is placed at 0.004 hPa, and there are 81 vertical levels. The Spectral Radiation-Transport Model for Aerosol Species (SPRINTARS) is used as an aerosol module for MIROC6 to predict the mass mixing ratios of the main tropospheric aerosols. By coupling the radiation and cloud-precipitation schemes, SPRINTARS calculates not only the aerosol transport processes but also the aerosol-radiation and aerosol-cloud interactions.The land surface model is based on Minimal Advanced Treatments of Surface Interaction and Runoff (MATSIRO), which includes a river routing model based on a kinematic wave flow equation and a lake module where one-dimensional thermal diffusion and mass conservation are considered. The horizontal resolution of the land surface model is the same as that of the atmopheric component. There are a three-layers snow and a six-layers soil down to a 14 m depth.The sea ice-ocean model is based on the CCSR Ocean Component model (COCO). The tripolar horizontal coordinate system is adopted, and the longitudinal grid spacing is 1° and the meridional grid spacing varies from about 0.5° near the equator to 1° in the mid-latitudes. There are 62 vertical levels in a hybrid σ-z coordinate system. A coupler system calculates heat and freshwater fluxes between the sub-models in order to ensure that all fluxes are conserved within machine precision and then exchanges the fluxes among the sub-models. No flux adjustments are used in MIROC6.
    flux correction - details > No flux corrections are applied in this model.
    genealogy - year released > 2018
    genealogy - CMIP3 parent > MIROC3m
    genealogy - CMIP5 parent > MIROC5
    genealogy - CMIP5 differences > Major changes from MIROC5, which was our official model for the CMIP5, to MIROC6 are mainly done in the atmospheric component. These include implementation of a parameterization of shallow convective processes, the higher model top and vertical resolution in the stratosphere. The ocean and land-surface components have been also updated in terms of the horizontal grid coordinate system and higher vertical resolution in the former, and parameterizations for sub-grid scale snow distribution and wet lands due to snow-melting water in the latter.
    genealogy - previous name > MIROC5
    software properties - repository > Shared repository on a server at Japan Agency for Marine-Earth Science and Technology
    software properties - code version > fe6402342aec
    software properties - code languages > Basically FORTRAN77 but partially FORTRAN90 and C
    software properties - components structure > The atmoshperic component and the ocean component are executed separately with a multiprogram-multiple data application. Note that a executable binary of the land surface component is included that of the atmospheric component. These submodels are coupled with time interval of 1 hour.
    software properties - coupler > Other: Original couplers: A coupler system calculates heat and freshwater fluxes between the sub-models in order to ensure that all fluxes are conserved within machine precision and then exchanges the fluxes among the sub-models. Details are described in Suzuki et al. (2009).
    coupling - atmosphere double flux > True
    coupling - atmosphere fluxes calculation grid > Specific coupler grid
    coupling - atmosphere relative winds > True
    tuning applied - description > In the first model tuning step, climatology, seasonal progression, and internal climate variability in the tropical coupled system are tuned in order that departures from observations or reanalysis datasets are reduced. Specifically, parameters of reference height for cumulus precipitation, efficiency of the cumulus entrainment of surrounding environment and maximum cumulus updraft velocity at the cumulus base are used to tune strength of the equatorial trade wind, climatological position and intensity of the Inter-Tropical Convergence Zone and South Pacific Convergence Zone, and interannual variability of El-Niño/Southern Oscillation. Summertime precipitation in the western tropical Pacific and characteristic of tropical intraseasonal oscillations are tuned by using the parameter for shallow convection describing the partitioning of turbulent kinetic energy between horizontal and vertical motions at the sub-cloud layer inversion. Next, the wintertime mid-latitude westerly jets and the stationary waves in the troposphere are tuned using the parameters of the orographic gravity wave drag and the hyper diffusion of momentum. The parameters of the hyper diffusion and the non-orographic gravity wave drag are also used when tuning stratospheric circulations of the polar vortex and Quasi Biennial Oscilation. Finally, the radiation budget at the TOA is tuned, primarily using the parameters for the auto-conversion process so that excess downward radiation can be minimized and maintained closer to 0.0 Wm-2. In addition, parameter tuning for the total radiative forcing associated with aerosol-radiation and aerosol-cloud interactions is done. In order that the total radiative forcing can be closer to the estimate of -0.9 Wm-2 (IPCC, 2013; negative value indicates cooling), parameters of cloud microphysics and the aerosol transport module, such as timescale for cloud droplet nucleation, in-cloud properties of aerosol removal by precipitation, and minimum threshold of number concentration of cloud droplets, are perturbed. To determine a suitable parameter set, several pairs of a present-day run under the anthropogenic aerosol emissions at the year 2000 and a pre-industrial run are conducted. A pair of the present and preindustrial runs has exactly the same parameters, and differences of tropospheric radiations between two runs are considered as anthropogenic radiative forcing.
    tuning applied - global mean metrics used > TOA radiation budget, radiative forcing, sea ice area
    tuning applied - regional metrics used > tropical precipiation, mid-latitude jets, ENSO amplitude, THC
    tuning applied - trend metrics used > HadCRU
    tuning applied - energy balance > The radiation budget at the TOA is tuned at the components coupling state.
    tuning applied - fresh water balance > Any tuninigs were done for fresh water balance.
    conservation - heat - global > Atmospheric heat is not conserved perffectly. The heat energy inconsistency is due to that internal energy associated with precipitation, water vapor and river runoff is not taken account in the atmospheric and land surface component in MIROC6.
    conservation - heat - atmos ocean interface > Heat flux is conserved during coupling procedures.
    conservation - heat - atmos land interface > Heat flux is conserved during coupling procedures.
    conservation - heat - atmos sea-ice interface > Heat flux is conserved during coupling procedures.
    conservation - heat - ocean seaice interface > Heat is conserved during coupling procedures.
    conservation - heat - land ocean interface > Temperature of river water is not considered thus there is no heat exchange between the land and the ocean.
    conservation - fresh water - global > Freshwater and salt are conserved.
    conservation - fresh water - atmos ocean interface > Freshwater flux is conserved during coupling procedures.
    conservation - fresh water - atmos land interface > Freshwater flux is conserved during coupling procedures.
    conservation - fresh water - atmos sea-ice interface > Freshwater flux is conserved during coupling procedures.
    conservation - fresh water - ocean seaice interface > Freshwater flux is conserved during coupling procedures.
    conservation - fresh water - iceberg calving > nan
    conservation - salt - ocean seaice interface > Salt is conserved during coupling procedures.
    name > MSTRNX
    overview > Greenhouse gases: CO2, CH4, N2O, Trop O3, Strat O3 Aerosols: SO4, BC, OC, dust, volcanic, sea salt, land use, solar Cloud albedo efffect : YES Cloud lifetime effect: YES
    greenhouse gases - CO2 - provision > Y
    greenhouse gases - CH4 - provision > Y
    greenhouse gases - N2O - provision > Y
    greenhouse gases - tropospheric O3 - provision > Y
    greenhouse gases - stratospheric O3 - provision > Y
    greenhouse gases - CFC - provision > Y
    greenhouse gases - CFC - equivalence concentration > Option 1
    aerosols - SO4 - provision > M
    aerosols - SO4 - additional information > DMS emission is diagnosed, and SO2 emission derived from biomass burning is prescribed.
    aerosols - black carbon - provision > E
    aerosols - organic carbon - provision > E
    aerosols - nitrate - provision > Y
    aerosols - cloud albedo effect - provision > E
    aerosols - cloud albedo effect - aerosol effect on ice clouds > True
    aerosols - cloud lifetime effect - provision > E
    aerosols - cloud lifetime effect - aerosol effect on ice clouds > True
    aerosols - cloud lifetime effect - RFaci from sulfate only > False
    aerosols - dust - provision > M
    aerosols - tropospheric volcanic - provision > C
    name > SPRINTARS
    keywords > aerosol transport,aerosol-radiation interaction,aerosol-cloud interaction
    overview > Spectral Radiation-Transport Model for Aerosol Species (SPRINTARS) predicts mass mixing ratios of the main tropospheric aerosols which are black carbon (BC), organic matter (OM), sulfate, soil dust, and sea salt, and the precursor gases of sulfate (sulfur dioxide and dimethylsulfide). SPRINTARS calculates not only the aerosol transport processes of emission, advection, diffusion, sulfur chemistry, wet deposition, dry deposition, and gravitational settling, but also the aerosol-radiation and aerosol-cloud interactions by coupled with the radiation and cloud-precipitation schemes in MIROC. See sections on model description in Takemura (2018, http://www.cger.nies.go.jp/publications/report/i138/i138.pdf) for furtther details.
    scheme scope > Troposphere
    basic approximations > ?
    prognostic variables form > 3D mass/volume ratio for aerosols
    number of tracers > 19
    family approach > True
    software properties - code languages > Fortran
    timestep framework - method > Uses atmospheric chemistry time stepping
    timestep framework - integrated timestep > 600
    timestep framework - integrated scheme type > Other
    resolution - name > T85L81h
    resolution - is adaptive grid > False
    tuning applied - description > Observational data on mass concentration of each aerosol comonent and aerosol optical thickness from satellite and in-situ are mainly used to tune the aerosol model. The aerosol radiative frocing which can simulated observed trend of the surface air temperature is also focued as a climate model.
    tuning applied - global mean metrics used > radiative forcing
    tuning applied - regional metrics used > aerosol optical thickness,mass concentration,Ångström exponent,aerosol single scattering albedo
    matches atmosphere grid > True
    resolution - name > T85L81h
    scheme > Specific transport scheme (semi-lagrangian)
    mass conservation scheme > Uses atmospheric chemistry transport scheme
    method > Prescribed (climatology)
    sources > Vegetation
    prescribed climatology > Constant
    interactive emitted species > soil dust,sea salt,DMS
    absorption - black carbon > 3.097
    absorption - organics > 0.1347
    mixtures - external > True
    mixtures - internal > True
    mixtures - mixing rule > A half of BC/OC from anthropogenic sources is internally mixed and the others are externally mixed.
    impact of h2o - size > True
    impact of h2o - internal mixture > True
    impact of h2o - external mixture > True
    radiative scheme - overview > The radiative process in MIROC is based on the two-stream discrete ordinate/adding method (Nakajima et al., 2000, doi:10.1364/AO.39.004869). In the radiation scheme, extinction and mass coefficients, asymmetry factor and truncation factor in each band are calculated for aerosols and clouds. The aerosol optical parameters are calculated according to the Mie theory and volume-weighted refractive indices with water for the internal mixture. The wavelength-dependent refractive indices are according to WCP-55 (1983, "Report of the experts meeting on aerosols and their climatic effects") for aerosols and d'Almeida et al. (1991, "Atmospheric Aerosols: Global Climatology and Radiative Characteristics") for water. See section 2.2 in Takemura (2018, http://www.cger.nies.go.jp/publications/report/i138/i138.pdf) for furtther details.
    radiative scheme - shortwave bands > 15
    radiative scheme - longwave bands > 14
    cloud interactions - overview > A parameterization based on the Köhler theory is introduced for water cloud (Ghan et al., 1997, doi:10.1029/97JD01810; Abdul-Razzak and Ghan, 2000, doi:10.1029/1999JD901161). The cloud droplet effective radius related with the Twomey effect is calculated depending on the prognostic cloud droplet number concentration and cloud water mixing ratio. The Berry's parameterization is adopted for the autoconversion process. The ice crystal number concetration is also treated as a prognostic variable. The homogeneous and heterogeneous freezings are based on Kärcher and Lohmann (2002, doi:10.1029/2001JD000470) and Lohmann and Diehl (2006, doi:10.1175/JAS3662.1), respectively. See section 3.2 in Takemura (2018, http://www.cger.nies.go.jp/publications/report/i138/i138.pdf) for furtther details.
    cloud interactions - twomey > True
    cloud interactions - twomey minimum ccn > 1
    cloud interactions - drizzle > False
    cloud interactions - cloud lifetime > True
    name > SPRINTARS
    overview > Spectral Radiation-Transport Model for Aerosol Species (SPRINTARS) predicts mass mixing ratios of the main tropospheric aerosols which are black carbon (BC), organic matter (OM), sulfate, soil dust, and sea salt, and the precursor gases of sulfate (sulfur dioxide and dimethylsulfide). SPRINTARS calculates not only the aerosol transport processes of emission, advection, diffusion, sulfur chemistry, wet deposition, dry deposition, and gravitational settling, but also the aerosol-radiation and aerosol-cloud interactions by coupled with the radiation and cloud-precipitation schemes in MIROC. See sections on model description in Takemura (2018, http://www.cger.nies.go.jp/publications/report/i138/i138.pdf) for furtther details.
    processes > Dry deposition
    coupling > Radiation
    gas phase precursors > DMS
    scheme type > Bulk
    name > MIROC-AGCM
    keywords > MIROC, AGCM, spectral dynamical core, parameterizations
    overview > MIROC-AGCM is the atmospheric component of a climate model, the Model for Interdisciplinary Research on Climate version 6 (MIROC6). The MIROC-AGCM employs a spectral dynamical core, and standard physical parameterizations for cumulus convections, radiative transfer, cloud microphysics, turbulence, and gravity wave drag. It also has an aerosol module. The model is cooperatively developed by the Japanese modeling community including the Atmosphere and Ocean Research Institute, the University of Tokyo, the Japan Agency for Marine-Earth Science and Technology, and the National Institute for Environmental Studies.
    model family > AGCM: Atmospheric General Circulation Model
    basic approximations > Primitive equations
    resolution - horizontal resolution name > T85
    resolution - canonical horizontal resolution > 1.4 x 1.4 degrees lat-lon
    resolution - range horizontal resolution > 1.4 deg globally
    resolution - number of vertical levels > 81
    resolution - high top > True
    timestepping - timestep dynamics > 360
    orography - type > Fixed
    tuning applied - description > MIROC-AGCM is coupled with the land surface and the sea ice-ocean components before the tuning under the pre-industrial boundary conditions. In the first model tuning step, climatology, seasonal progression, and internal climate variability in the tropical coupled system are tuned in order that departures from observations or reanalysis datasets are reduced. Representation of the tropical system in MIROC6 is sensitive to the parameters for cumulus convection and planetary boundary layer processes. Next, the wintertime mid-latitude westerly jets and the stationary waves in the troposphere are tuned using the parameters of the orographic gravity wave drag and the hyper diffusion of momentum. The parameters of the hyper diffusion and the non-orographic gravity wave drag are also used when tuning stratospheric circulations of the polar vortex and QBO. Finally, the radiation budget at the TOA is tuned, primarily using the parameters for the auto-conversion process. The surface albedos for bare sea-ice and snow-covered sea-ice are set to higher values than in observations in order to avoid underestimating of the summertime sea-ice extent in the Arctic Ocean due to excess downward shortwave radiation in this region. In addition, parameter tuning for cooling effects due to interactions between anthropogenic aerosol emissions and cloud-radiative processes are done. In order that the cooling effects can be closer to the estimate of -0.9 W/m^2 (IPCC, 2013; negative value indicates cooling) with an uncertainty range of -1.9 to -0.1 W/m^2, parameters of cloud microphysics and the aerosol transport module are perturbed.
    name > MATSIRO6
    keywords > land surface model, big leaf model, multi-layer snow scheme, TOPMODEL-based approach
    description > Surface energy balance, radiative transfer in canopy, stomatal resistance, canopy interception, snow hydrology, prognostic snow albedo, runoff generation, soil hydrology and soil temperature.
    land atmosphere flux exchanges > Water
    atmospheric coupling treatment > implicit
    land cover > Land ice
    land cover change > Net transition between potential vegetation cover and cropland is considered.
    tiling > Each land grid has three tiles: potential vegetation, cropland, and lake. We use annual potential vegetation and cropland fractions from Land-Use Harmonization (LUH2); managed pasture, C3 annual crops, C3 perennial crops, C4 annual crops, C4 perennial crops and C3 nitrogen-fixing crops are categorized as cropland.The potential vegetation and cropland tiles are divided into two areas with and without snow cover. The lake is also divided into ice-covered and open water areas. The land surface fluxes are calculated in each area and averaged, weighted by their fractions. The land/sea fraction is considered.
    conservation properties - energy > Energy is conserved globally at land surface.
    conservation properties - water > Water is conserved globally except for land ice grids.
    conservation properties - carbon > nan
    timestepping framework - timestep dependent on atmosphere > True
    timestepping framework - time step > 1
    timestepping framework - timestepping method > Variable atmosphere time step and 3600 seconds are used for flux calculation and land integration, respectively
    software properties - code languages > FORTRAN
    overview > Atmosphere horizontal grid is used for the land model.
    horizontal - description > Atmosphere horizontal grid is used.
    horizontal - matches atmosphere grid > True
    vertical - description > Soil has six layers with a thickness of 0.05, 0.2, 0.75, 1, 2, and 10 m.
    overview > The soil parameterization includes soil hydrology, soil temperature prediction, and TOPMODEL-based runoff parameterization with six soil layers. The soil parameters depend on soil texture from ISLSCP I.
    heat water coupling > Heat and water is coupled through soil freeze and thaw processes.
    number of soil layers > 6
    prognostic variables > Soil temperature, Soil moisture, Soil ice content
    soil map - description > The soil texture map based on ISLSCP Initiative I is used.
    soil map - structure > ISLSCP Initiative I (FAO, GISS, U. Arizona, NASA/GSFC)
    soil map - texture > ISLSCP Initiative I (FAO, GISS, U. Arizona, NASA/GSFC)
    soil map - organic matter > nan
    soil map - albedo > ISLSCP Initiative I (ERBE)
    soil map - water table > N/A. Water table is diagnosed in the model.
    soil map - continuously varying soil depth > False
    soil map - soil depth > N/A. Soil depth is constant.
    snow free albedo - prognostic > True
    snow free albedo - functions > Vegetation state
    snow free albedo - direct diffuse > Distinction between direct and diffuse albedo
    snow free albedo - number of wavelength bands > 3
    hydrology - description > The unfrozen soil moisture is predicted by the Richards equation with hydraulic properies based on Clapp and Hornberger (1979).
    hydrology - time step > 180
    hydrology - tiling > nan
    hydrology - vertical discretisation > Soil has six layers with a thickness of 0.05, 0.2, 0.75, 1, 2, and 10 m.
    hydrology - number of ground water layers > 6
    hydrology - lateral connectivity > Other: No connectivity
    hydrology - method > Explicit diffusion
    hydrology - freezing - number of ground ice layers > 6
    hydrology - freezing - ice storage method > Thermo dynamics
    hydrology - freezing - permafrost > There is no specific treatment for permafrost. But near-surface permafrost is represented by soil freezing processes.
    hydrology - drainage - description > Runoff is calculated following a simplified TOPMODEL.
    hydrology - drainage - types > Horton mechanism
    heat treatment - description > The soil temperature is predicted by a heat conduction equation with a zero heat flux at the bottom. The soil moisture freeze and thaw processes are included.
    heat treatment - time step > 3600
    heat treatment - tiling > Tiling corresponded to potential vegetation /cropland tiling.
    heat treatment - vertical discretisation > Soil has six layers with a thickness of 0.05, 0.2, 0.75, 1, 2, and 10 m.
    heat treatment - heat storage > Explicit diffusion
    overview > The snow parameterization includes snow accumulation, snowmelt, and refreeze of snowmelt and rainfall with up to three snow layers. Snow temperature is calculated by a heat conduction equation. SSNOWD (Liston, 2004) snow cover fraction parameterization, which assumes a subgrid snow distribution function, is implemented.
    tiling > Tiling corresponded to potential vegetation/cropland tiling.
    number of snow layers > 3
    density > Constant
    water equivalent > Prognostic
    heat content > Diagnostic
    temperature > Prognostic
    liquid water content > Other: N/A
    snow cover fractions > Ground snow fraction
    processes > Snow interception
    prognostic variables > Snow mass, Snow temperature, Snow albedo, Dust density in snow, Accumulated snow mass in the absence of any melt, Accumulated snow water-equivalent melt depth
    snow albedo - type > Prognostic
    overview > Monthly leaf area index from MODIS is used to represent vegetation phenology. Stomatal Resistance from SiB2 based photosynthesis scheme is used to calculate transpiration. Canopy interception is considered.
    dynamic vegetation > False
    tiling > Tiling of potential vegetaion cover and cropland is considered.
    vegetation representation > Vegetation types
    vegetation types > C3 grass
    biome types > Evergreen broadleaf forest
    vegetation time variation > Fixed (not varying)
    vegetation map > Watanabe_2010
    interception > True
    phenology > Other: Prescribed
    phenology description > Monthly leaf area index for cropland and potential vegetation cover is derived from MODIS LAI (Myneni et al., 2015) and land cover type (Friedl et al., 2010).
    leaf area index > Prescribed
    leaf area index description > Monthly leaf area index for cropland and potential vegetation cover is derived from MODIS LAI (Myneni et al., 2015) and land cover type (Friedl et al., 2010).
    biomass > Other: N/A
    biomass description > nan
    biogeography > Other: N/A
    biogeography description > nan
    stomatal resistance > CO2
    stomatal resistance description > Stomatal resistance is calculated using a photosynthetic scheme after SiB2 (Selleres et al., 1996).
    overview > The surface energy balance is calculated by linearization of surface temperature equations for canopy and surface. The canopy albedo and transmissivity are calculated using simplified radiative transfer in canopy by Watanabe and Ohtani (1995). The bulk coefficients are estimated based on Watanabe (1994).
    tiling > The energy balance is calculated for snow-covered and snow-free surface of each tile.
    number of surface temperatures > 4
    evaporation > Other: Alpha for soil evaporation, Beta for transpiration
    name > SiB2
    overview > Diagnose CO2 flux associated with photosynthesis and leaf respiration
    tiling > nan
    vegetation - number of carbon pools > 0
    vegetation - forest stand dynamics > nan
    vegetation - photosynthesis - method > SiB2 (Sellers et al 1996). Different parameters for C3 and C4 grasses according to ISLSCP 1.
    vegetation - autotrophic respiration - maintainance respiration > SiB2 (Sellers et al 1996)
    vegetation - autotrophic respiration - growth respiration > nan
    vegetation - allocation - method > nan
    vegetation - phenology - method > Prescribed LAI
    vegetation - mortality - method > nan
    litter - number of carbon pools > 0
    litter - carbon pools > nan
    litter - decomposition > nan
    litter - method > nan
    soil - number of carbon pools > 0
    soil - carbon pools > nan
    soil - decomposition > nan
    soil - method > nan
    permafrost carbon - is permafrost included > False
    permafrost carbon - emitted greenhouse gases > nan
    permafrost carbon - decomposition > nan
    name > nan
    name > TRIP2
    overview > The river routing model is TRIP2 which is based on Oki and Sud (1998) with a kinematic wave flow equation (Ngo-Duc et al 2007). It is the same as the model for CMIP5, but the river network map is updated (Yamazaki et al., 2009).
    tiling > River discharge and ice flow are considered.
    time step > 3600
    grid inherited from land surface > True
    grid description > The grid is inherited from land surface
    number of reservoirs > 2
    coupled to atmosphere > False
    coupled to land > Runoff from all land tiles averaged with their fractions flows into rivers.
    basin flow direction map > Present day
    flooding > nan
    prognostic variables > River water storage
    oceanic discharge - discharge type > Direct (large rivers)
    overview > The lake model considers vertical thermal diffusion and mass conservation. It is the same as the previous version of the model used for CMIP5.
    coupling with rivers > True
    time step > 3600
    quantities exchanged with rivers > Water
    vertical grid > Lake has five layers with a variable thickness depending on lake level.
    prognostic variables > Lake temperature, Lake salinity, Lake ice surface temperature, Lake ice concentration, Lake ice thickness, Lake snow thickness, Lake level
    method - ice treatment > True
    method - albedo > Diagnostic
    method - dynamics > Vertical
    method - dynamic lake extent > True
    method - endorheic basins > True
    name > COCO4.9
    keywords > Primitive equation, hydrostatic, Boussinesq, explicit free surface, tripolar grid, sigma-z hybrid, embedded sea-ice component
    overview > COCO is an ice-ocean coupled model which can be used as a stand-alone model or an ice-ocean component of MIROC. It has been developed in Atmosphere and Ocean Research Institute (AORI), The University of Tokyo, and Japan Agency for Marine-Earth Science and Technology (JAMSTEC). The oceanic part of COCO is based on the primitive equations under the hydrostatic and Boussinesq approximations with the explicit free surface and is formulated on the generalized curvilinear horizontal coordinate and the geopotential height vertical coordinate with optional sigma coordinate near the surface.
    model family > OGCM
    basic approximations > Boussinesq
    prognostic variables > Potential temperature
    seawater properties - eos type > Mc Dougall et al.
    seawater properties - eos functional temp > Potential temperature
    seawater properties - eos functional salt > Practical salinity Sp
    seawater properties - eos functional depth > Depth (meters)
    seawater properties - ocean freezing point > Other
    seawater properties - ocean specific heat > 3990
    seawater properties - ocean reference density > 1000
    bathymetry - reference dates > Present day
    bathymetry - type > True
    bathymetry - ocean smoothing > Averaging when converting the original data (ETOPO1) into the model bathymetry. Editing some important seawater pathways, small islands, and small merginal seas.
    bathymetry - source > ETOPO1
    nonoceanic waters - isolated seas > The Mediterranean Sea is isolated and exchange water/heat/salt with the Atlantic Ocean as a form of diffusive flux. The Red Sea is treated as land in OGCM but 1-d mixed layer model in the land component.
    nonoceanic waters - river mouth > No specific treatment: put river discharge into the uppermost layer of the river mouth grid.
    software properties - repository > internal repository
    software properties - code version > 4.9
    software properties - code languages > Fortran 90
    resolution - name > COCO medium resolution model
    resolution - canonical horizontal resolution > 1 degree
    resolution - range horizontal resolution > 0.5 degree - 1 degree
    resolution - number of horizontal gridpoints > 92160
    resolution - number of vertical levels > 63
    resolution - is adaptive grid > False
    resolution - thickness level 1 > 2
    tuning applied - description > Our main target is to reproduce reasonable THC (in particular AMOC) strength and volume transport across some key starits/pathways. In addition, we also checked T/S fields in orde to avoid unrealistic long-term trends. We mainly modified ocean bathmetry rather than parameter-level tuning to retain these metrics.
    conservation - description > We have checked changes of the properties which should be conserved are in the range of numerical error by calculating the difference of these properties by using multiple snapshots of the modeled ocean.
    conservation - scheme > Salt
    name > COCO medium resolution model
    discretisation - vertical - coordinates > Hybrid / Z+S
    discretisation - vertical - partial steps > True
    discretisation - horizontal - type > Two north poles (ORCA-style)
    discretisation - horizontal - staggering > Arakawa B-grid
    name > Staggard timestepping
    diurnal cycle > Via coupling: Diurnal cycle via coupling frequency
    tracers - scheme > Other
    tracers - time step > 1200
    baroclinic dynamics - type > Other
    baroclinic dynamics - scheme > Other
    baroclinic dynamics - time step > 1200
    barotropic - splitting > Split explicit
    barotropic - time step > 20
    momentum - type > Flux form
    momentum - scheme name > centered-in-space differencing scheme
    momentum - ALE > False
    lateral tracers - order > 4
    lateral tracers - flux limiter > True
    lateral tracers - effective order > 1
    lateral tracers - name > Prather 2nd moment (PSOM)
    lateral tracers - passive tracers > Ideal age
    vertical tracers - name > Prather 2nd moment (PSOM)
    scheme > None: No transient eddies in ocean
    momentum - operator - direction > Horizontal
    momentum - operator - order > Harmonic: Second order
    momentum - operator - discretisation > Second order: Second order
    momentum - eddy viscosity coeff - type > Space varying
    momentum - eddy viscosity coeff - variable coefficient > depending on horizontal grid size
    momentum - eddy viscosity coeff - coeff background > 1.7e3 -- 2.3e4, space varying
    momentum - eddy viscosity coeff - coeff backscatter > False
    tracers - mesoscale closure > True
    tracers - submesoscale mixing > False
    tracers - operator - direction > Isopycnal
    tracers - operator - order > Harmonic: Second order
    tracers - operator - discretisation > Second order: Second order
    tracers - eddy diffusity coeff - type > Constant
    tracers - eddy diffusity coeff - constant coefficient > 1000
    tracers - eddy diffusity coeff - coeff background > 100
    tracers - eddy diffusity coeff - coeff backscatter > False
    tracers - eddy induced velocity - type > GM: Gent & McWilliams
    tracers - eddy induced velocity - constant val > 300
    tracers - eddy induced velocity - flux type > Skew flux
    boundary layer mixing - details - langmuir cells mixing > False
    boundary layer mixing - tracers - type > Turbulent closure - Mellor-Yamada
    boundary layer mixing - tracers - closure order > 2.5
    boundary layer mixing - tracers - background > Tsujino et al. (2000) type III
    boundary layer mixing - momentum - type > Turbulent closure - Mellor-Yamada
    boundary layer mixing - momentum - closure order > 2.5
    boundary layer mixing - momentum - background > 0.0001
    interior mixing - details - convection type > Non-penetrative convective adjustment
    interior mixing - details - tide induced mixing > none
    interior mixing - details - double diffusion > False
    interior mixing - details - shear mixing > False
    interior mixing - tracers - type > Other
    interior mixing - tracers - profile > True
    interior mixing - tracers - background > Tsujino et al. (2000) type III
    interior mixing - momentum - type > Constant value
    interior mixing - momentum - profile > False
    free surface - scheme > Other
    free surface - embeded seaice > False
    bottom boundary layer - overview > Nakano and Suginohara (2002) bottom boundary layer scheme is applied. Following this paper, it is applied at high latitudes, to the north of 49N and to the south of 56S.
    bottom boundary layer - type of bbl > Acvective
    surface pressure > Nothing specific
    momentum flux correction > When calculating the bulk coefficient of momentum flux, minimum wind speed is applied.
    tracers flux correction > When calculating the bulk coefficient of tracer fluxes, minimum wind speed is applied.
    wave effects > Nothing specific.
    river runoff budget > Apply river routing model (CaMa-Flood).
    geothermal heating > Not applied.
    momentum - bottom friction - type > Constant drag coefficient
    momentum - lateral friction - type > No-slip
    tracers - sunlight penetration - scheme > 2 extinction depth
    tracers - sunlight penetration - ocean colour > False
    tracers - sunlight penetration - extinction depth description > RADDN = RRR * EXP(- DEPTH / ZETA1) + (1.D0 - RRR) * EXP(- DEPTH / ZETA2), where RRR=0.58, ZETA1=0.35, ZETA2=23. unit:[m]
    tracers - sunlight penetration - extinction depths > 0.35 m, 23 m
    tracers - fresh water forcing - from atmopshere > Freshwater flux
    tracers - fresh water forcing - from sea ice > Other
    name > COCO4.9
    keywords > Subgrid-scale thickness distribution, 1-layer thermodynamics, EVP rheology
    overview > COCO is an ice-ocean coupled model which can be used as a stand-alone model or an ice-ocean component of MIROC. It has been developed in Atmosphere and Ocean Research Institute (AORI), The University of Tokyo, and Japan Agency for Marine-Earth Science and Technology (JAMSTEC). The sea-ice part of COCO employs subgrid-scale thickness distribution, 1-layer thermodynamics, and EVP rheology.
    variables - prognostic > Sea ice concentration
    seawater properties - ocean freezing point > Other
    resolution - name > COCO medium resolution model
    resolution - canonical horizontal resolution > 1 degree
    resolution - number of horizontal gridpoints > 92160
    tuning applied - description > Our primary target of tuning to retain reasonable sea-ice extent in each hemisphere and realistic horizontal distribution of sea-ice concentration/thickness. Climate performance metrics generally take priority. Note that most of the parameters in other submodels are tuned mainly for improving global climate processes rather than sea-ice states. Sea-ice and snow on the ice have quite a high albedo to enhance the reproducibility with the other submodels' setting.
    tuning applied - target > sea ice minima in NH, sea ice maxima in SH, and reasonable horizontal distibution
    tuning applied - simulations > pi-control only
    tuning applied - variables > albedo-related paramters
    key parameter values - ice strength > 20000
    key parameter values - snow conductivity > 0.31
    key parameter values - ice thickness in leads > 0.3
    key parameter values - additional parameters > maximum concentration in a specific grid: 0.99
    assumptions - description > Ice thinner than minimum thickness, 0.3 m, is not allowed to exist. Snow area fraction over sea ice is not explicitly handled; instead, albedo dependency on skin temperature and snow thickness implicitly includes the effect of snow area fraction change.
    assumptions - on diagnostic variables > Some of variables such as snow area fraction is not defined
    assumptions - missing processes > Melt pond is not represented. Rainfall as a form of water directly falls into the ocean and does not interact with the sea-ice component.
    conservation - description > We have checked changes of the properties which should be conserved are in the range of numerical error by calculating the difference of these properties by using multiple snapshots of the modeled ocean.
    conservation - properties > Mass
    conservation - budget > Mass, sea-ice mass per area, snow mass per area. Salt, sea-ice mass per area.
    conservation - was flux correction used > False
    discretisation - horizontal - grid > Ocean grid: Sea ice is horizontally discretised on the ocean grid.
    discretisation - horizontal - grid type > Structured grid
    discretisation - horizontal - scheme > Finite differences
    discretisation - horizontal - thermodynamics time step > 1200
    discretisation - horizontal - dynamics time step > 80
    discretisation - vertical - layering > Other
    discretisation - vertical - number of layers > 1
    seaice categories - has mulitple categories > True
    seaice categories - number of categories > 5
    seaice categories - category limits > 0.3, 0.6, 1.0, 2.5, 5.0
    seaice categories - ice thickness distribution > The governing equation follows Thorndike et al. (1975). Its discritizaion as well as the evaluation of mechanical redistribution term follows Bitz et al. (2001).
    snow on seaice - has snow on ice > True
    snow on seaice - number of snow levels > 1
    snow on seaice - snow fraction > Snow area fraction is not explicitly handled; instead, albedo dependency on skin temperature and snow thickness implicitly includes the effect of snow area fraction change.
    horizontal transport > Eulerian
    transport in thickness space > Other
    ice strength formulation > Hibler 1979
    redistribution > Ridging
    energy - enthalpy formulation > Pure ice latent and sensible heat + explicit brine inclusions (Bitz and Lipscomb)
    energy - thermal conductivity > Pure ice
    energy - heat diffusion > Conduction fluxes
    energy - basal heat flux > Other
    energy - fixed salinity value > 5
    energy - heat content of precipitation > Precipitation as a form of water directly falls into the ocean and does not interact with the sea-ice component.
    mass - new ice formation > From open water
    mass - ice vertical growth and melt > From open water, bottom, and lateral
    mass - ice lateral melting > Other
    mass - ice surface sublimation > Sublimation flux is diagnosed in the coupler to the atmospheric component.
    mass - frazil ice > New ice formation from open water implicitly includes frazil ice formation.
    salt - has multiple sea ice salinities > False
    salt - sea ice salinity thermal impacts > True
    salt - mass transport - salinity type > Constant
    salt - mass transport - constant salinity value > 5
    salt - thermodynamics - salinity type > Constant
    salt - thermodynamics - constant salinity value > 5
    ice thickness distribution - representation > Explicit
    ice floe size distribution - representation > Parameterised
    melt ponds - are included > False
    melt ponds - formulation > Other
    snow processes - has snow aging > False
    snow processes - has snow ice formation > True
    snow processes - snow ice formation scheme > When snow-ice interface comes below sea level, the snow between the interface and sea level turns into sea ice.
    snow processes - redistribution > Snow-ice
    surface albedo > Other


This time we can use directly one function **get_doc()**. It gets three
arguments: \* the kind of document, can be model, experiment or mip; \*
the name of the model, experiment or mip; \* project for which I want to
retrieve the document, by default this is CMIP6. It will retrieve the
document online and print out a summary. It will also return the url for
the full document report, shown below.

.. code:: ipython3

    print(doc_url)


.. parsed-literal::

    https://api.es-doc.org/2/document/search-name?client=ESDOC-VIEWER-DEMO&encoding=html&project=CMIP6&name=MIROC6&type=CIM.2.SCIENCE.MODEL


ESDOC works only for CMIP6 and newer ESGF datasets. The World data
Center for Climate (WDCC) website holds documentation for both CMIP6 and
CMIP5, the **get_wdcc()** function access these documents. In this case
rather than the type of document you have to use the datset_id to
retrieve the information.

.. code:: ipython3

    doc_url, response = get_wdcc('cmip5.output1.MIROC.MIROC5.historical.mon.atmos.Amon.r1i1p1.v20111028')
    print(doc_url)
    print(response['response']['docs'])


.. parsed-literal::

    https://cera-www.dkrz.de/WDCC/ui/cerasearch/solr/select?rows=1&wt=json&q=entry_name_s:cmip5*output1*MIROC*MIROC5
    [{'geo': ['ENVELOPE(-180.00, 180.00, 90.00,-90.00)'], 'accuracy_report_s': 'not filled', 'specification_s': 'not filled', 'completeness_report_s': 'not filled', 'entry_type_s': 'experiment', 'qc_institute_s': 'MIROC', 'summary_s': 'MIROC data of the MIROC5 model as contribution for CMIP5 - Coupled Model\nIntercomparison Project Phase 5 (https://pcmdi.llnl.gov/mips/cmip5).\nExperiment design is described in detail in\nhttps://pcmdi.llnl.gov/mips/cmip5/experiment_design.html and the list of output\nvariables and their temporal resolutions are given in\nhttps://pcmdi.llnl.gov/mips/cmip5/datadescription.html . The output is stored in netCDF\nformat as time series per variable in model grid spatial resolution. For more information\non the Earth System model and the simulation please refer to the CIM repository.', 'general_key_ss': ['CMIP5', 'IPCC', 'IPCC-AR5', 'IPCC-DDC', 'MIROC5', 'climate simulation'], 'entry_name_s': 'cmip5 output1 MIROC MIROC5', 'date_range_rdt': '[1960-01 TO 2669-12]', 'progress_acronym_s': 'completely archived', 'consistency_report_s': 'not filled', 'additional_infos_ss': ['standard_output.pdf', 'Taylor_CMIP5_design.pdf'], 'creation_date_dt': '2012-01-13T14:54:16Z', 'project_acronym_ss': ['IPCC-AR5_CMIP5'], 'authors_s': 'MIROC', 'model_s': 'MIROC5', 'id': '2320274', 'entry_acronym_s': 'MIM5', 'project_name_ss': ['IPCC-AR5_CMIP5 (IPCC Assessment Report 5 and Coupled Model Intercomparison Project data sets)'], 'hierarchy_steps_ss': ['IPCC-AR5_CMIP5', 'MIM5'], 'access_s': 'http://cera-www.dkrz.de/WDCC/CMIP5/Compact.jsp?acronym=MIM5', 'hierarchy_ss': ['project @ 2 @ IPCC-AR5_CMIP5 @ '], '_version_': 1650056364700991488, 'score': 1.0}]


We are still working to add a function that will give a formatted print
of the wdcc documents as for the the ESDOC ones.

More on queries
~~~~~~~~~~~~~~~

About experiment_family
^^^^^^^^^^^^^^^^^^^^^^^

Experiment_family is a facet present only for CMIP5, it allows you to
select all the experiments following in the same category. The
correspondent in CMIP6 is activity. However, not all experiments belong
to a family and searching for both experiment and experiment_family at
the same time can give unexpected results. Let’s look at an example, if
I want to get all the rcps experiments and historical I might be tempted
to pass them as constraints in the same query:

.. code:: ipython3

    !clef cmip5 -m CMCC-CM -e historical --experiment_family RCP -t Omon -v tos -en r1i1p1


.. parsed-literal::

    None
    No matches found on ESGF, check at https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5&ensemble=r1i1p1&experiment=historical&model=CMCC-CM&cmor_table=Omon&variable=tos&experiment_family=RCP


We couldn’t find any matches because both constraints have to be true,
similarly if we pass rcp45 as experiment as well as the family RCP we
will only get the rcp45 results.

.. code:: ipython3

    !clef cmip5 -m CMCC-CM -e rcp45 --experiment_family RCP -t Omon -v tos -en r1i1p1


.. parsed-literal::

    None
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20120518/tos/
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20170725/tos/
    
    Everything available on ESGF is also available locally


Finally, it is now possible to use experiment_family also in the local
search:

.. code:: ipython3

    !clef --local cmip5 -m CMCC-CM --experiment_family RCP -t Omon -v tos -en r1i1p1


.. parsed-literal::

    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20120518/tos
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20170725/tos
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp85/mon/ocean/Omon/r1i1p1/v20120528/tos
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp85/mon/ocean/Omon/r1i1p1/v20170725/tos


Searching for other climate datasets: ds
----------------------------------------

Let’s get back to the command line now and have a look at the third
command **ds**\  This command let you query a separate database that
contains information on other climate datasets which are available on
raijin.

.. code:: ipython3

    !clef ds --help


.. parsed-literal::

    Usage: clef ds [OPTIONS]
    
      Search local database for non-ESGF datasets
    
    Options:
      -d, --dataset TEXT              Dataset name
      -v, --version TEXT              Dataset version
      -f, --format [netcdf|grib|HDF5|binary]
                                      Dataset file format as defined in clef.db
                                      Dataset table
      -sn, --standard-name [air_temperature|air_pressure|rainfall_rate]
                                      Variable standard_name this is the most
                                      reliable way to look for a variable across
                                      datasets
      -cn, --cmor-name [ps|pres|psl|tas|ta|pr|tos]
                                      Variable cmor_name useful to look for a
                                      variable across datasets
      -va, --variable [T|U|V|Z]       Variable name as defined in files: tas, pr,
                                      sic, T ...
      --frequency [yr|mon|day|6hr|3hr|1hr]
                                      Time frequency on which variable is defined
      --from-date TEXT                To define a time range of availability of a
                                      variable,
                                      can be used on its own or together
                                      with to-date. Format is YYYYMMDD
      --to-date TEXT                  To define a time range of availability of a
                                      variable,
                                      can be used on its own or together
                                      with from-date. Format is YYYYMMDD
      --help                          Show this message and exit.


| clef ds
| with no other argument will return a list of the local datasets
  available in the database. NB this is not an exhaustive list of the
  climate collections at NCI and not all the datasets already in the
  database have been completed.

.. code:: ipython3

    !clef ds


.. parsed-literal::

    ERA5 v1.0: /g/data/ub4/era5/netcdf/<stream>/<varname>/<year>/
    MACC v1.0: /g/data/ub4/macc/grib/<stream>/
    YOTC v1.0: /g/data/rq7/yotc
    ERAI v1.0: /g/data/ub4/erai/netcdf/<frequency>/<realm>/<stream>/<version>/<varname>/
    OSTIA vNA: /g/data/ua8/ostia
    TRMM_3B42 v7: /g/data/ua8/NASA_TRMM/TRMM_L3/TRMM_3B42/<YYYY>/
    OISST v2.0: /g/data/ua8/NOAA_OISST/AVHRR/v2-0_modified/
    MERRA2 v5.12.4: /g/data/rr7/MERRA2/raw/<streamv1>.<version>/<YYYY>/<MM>/
    ERAI v1.0: /g/data/ub4/erai/netcdf/<frequency>/<realm>/<stream>/v01/<varname>/
    MACC v1.0: /g/data/ub4/macc/netcdf/<frequency>/<realm>/<stream>/v01/<varname>/
    YOTC v1.0: /g/data/rq7/yotc


If you specify any of the variable options then the query will return a
list of variables rather then datasets. Since variables can be named
differently among datasets, using the *standard_name* or *cmor_name*
options to identify them is the best option.

.. code:: ipython3

    !clef ds -f netcdf --standard-name air_temperature


.. parsed-literal::

    2T: /g/data/ub4/era5/netcdf/surface/2T/<year>/2T_era5_-90 90 -180 179.75_<YYYYMMDD>_<YYYYMMDD>.nc
    T: /g/data/ub4/era5/netcdf/pressure/T/<year>/T_era5_-57 20 78 -140_<YYYYMMDD>_<YYYYMMDD>.nc
    2T: /g/data/ub4/era5/netcdf/surface/2T/<year>/2T_era5_-90 90 -180 179.75_<YYYYMMDD>_<YYYYMMDD>.nc
    T: /g/data/ub4/era5/netcdf/pressure/T/<year>/T_era5_-57 20 78 -140_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/1.0/ta/ta_6hr_ERAI_historical_oper_an_pl_<YYYYMMDD>_<YYYYMMDD>.nc
    tas: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_sfc/1.0/tas/tas_6hr_ERAI_historical_oper_an_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_ml/1.0/ta/ta_6hr_ERAI_historical_oper_an_ml_<YYYYMMDD>_<YYYYMMDD>.nc
    mn2t: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/mn2t/mn2t_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
    mx2t: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/mx2t/mx2t_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
    tas: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/tas/tas_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc


This returns all the variable available as netcdf files and with
air_temperature as standard_name. NB for each variable a path structure
is returned.

.. code:: ipython3

    !clef ds -f netcdf --cmor-name ta


.. parsed-literal::

    T: /g/data/ub4/era5/netcdf/pressure/T/<year>/T_era5_-57 20 78 -140_<YYYYMMDD>_<YYYYMMDD>.nc
    T: /g/data/ub4/era5/netcdf/pressure/T/<year>/T_era5_-57 20 78 -140_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/1.0/ta/ta_6hr_ERAI_historical_oper_an_pl_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_ml/1.0/ta/ta_6hr_ERAI_historical_oper_an_ml_<YYYYMMDD>_<YYYYMMDD>.nc


This returns a subset of the previous query using the cmor_name to
clearly identify one kind of air_temperature.

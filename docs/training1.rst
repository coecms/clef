Using CleF - Climate Finder to discover ESGF data at NCI
========================================================

This is a transcript of the clef_demo.ipynb training notebook available on github.

CleF is currently installed in the CMS conda module analysis3, or
analysis3-unstable for the latest version. This is managed by the CMS
and is available simply by running > module use
/g/data3/hh5/public/modules > module load conda/analysis3

You need to be a member of hh5 to use the modules and of one of the CMIP
projects: oi10,rr3, fs38, al33 to access the data and the clef database.
You could use the module interactively, for the moment we will use its
command line options. Let’s start!

Command syntax
--------------

.. code:: ipython3

    # run this if you haven't done so already in the terminal
    #!module use /g/data3/hh5/public/modules
    #!module load conda/analysis3-unstable

.. code:: ipython3

    !clef


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
      cmip5   Search ESGF and local database for CMIP5 files Constraints can be...
      cmip6   Search ESGF and local database for CMIP6 files Constraints can be...
      cordex  Search ESGF and local database for CORDEX files.
      ds      Search local database for non-ESGF datasets


By simpling running the command **clef** with no arguments, the tool
shows the help message and then exits, basically it is equivalent to >
clef –help

We can see currently there are 4 sub-commands, **ds** to query non-ESGF
collections and one for each ESGF dataset: **cmip5**, **cordex** and
**cmip6**. There are also five different options that can be passed
before the sub-commands, one we have already seen is ``--help``. The
others are used to modify how the tool will deal with the main query
output. We will have a look at them and at **ds** later. Let’s start
from quering some CMIP5 data, to see what we can pass to the **cmip5**
sub-command we can simply run it with its ``--help`` option.

CMIP5
-----

.. code:: ipython3

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
      --cf_standard_name TEXT         CF variable standard_name, use instead of
                                      variable constraint
    
      --and [variable|experiment|cmor_table|realm|time_frequency|model|ensemble]
                                      Attributes for which we want to add AND
                                      filter, i.e. `--and variable` to apply to
                                      variable values
    
      --institution TEXT              Modelling group institution id: MIROC, IPSL,
                                      MRI ...
    
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


Passing arguments and options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--help`` shows all the constraints we can pass to the tool, there
are also some additional options which can change the way we run our
query. For the moment we can ignore these and use their default values.
Some of the constraints can be passed using an abbreviation,like ``-v``
instead of ``--variable``. This is handy once you are more familiar with
the tool. The same option can have more than one name, for example
``--ensemble`` can also be passed as ``--member``, this is because the
terminology has changed between CMIP5 and CMIP6. You can pass how many
constraints you want and pass the same constraint more than once. Let’s
see what happens though if we do not pass any constraint.

.. code::

    !clef cmip5


.. parsed-literal::

    ERROR: Too many results (3781387), try limiting your search https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5


.. code::

    !clef cmip5 --variable tasmin --experiment historical --table day --ensemble r2i1p1s


.. parsed-literal::

    ERROR: No matches found on ESGF, check at https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5&ensemble=r2i1p1s&experiment=historical&cmor_table=day&variable=tasmin


Oops that wasn’t reasonable! I mispelled the ensemble “r2i1p1s” does not
exists and the tool is telling me it cannot find any matches.

.. code::

    !clef cmip5 --variable tasmin --experiment historical --table days --ensemble r2i1p1


.. parsed-literal::

    Usage: clef cmip5 [OPTIONS] [QUERY]...
    Try 'clef cmip5 --help' for help.
    
    Error: Invalid value for '--table' / '--mip' / '-t': invalid choice: days. (choose from Amon, Omon, OImon, LImon, Lmon, 6hrPlev, 6hrLev, 3hr, Oclim, Oyr, aero, cfOff, cfSites, cfMon, cfDay, cf3hr, day, fx, grids)


Made another spelling mistake, in this case the tool knows that I passed
a wrong value and lists for me all the available options for the CMOR
table. Eventually we are aiming to validate all the arguments we can,
although for some it is no possible to pass all the possible values
(ensemble for example).

.. code::

    !clef cmip5 --variable tasmin --experiment historical --table day --ensemble r2i1p1


.. parsed-literal::

    /g/data/al33/replicas/CMIP5/combined/CCCma/CanCM4/historical/day/atmos/day/r2i1p1/v20120207/tasmin/
    /g/data/al33/replicas/CMIP5/combined/CCCma/CanCM4/historical/day/atmos/day/r2i1p1/v20120612/tasmin/
    /g/data/al33/replicas/CMIP5/combined/CCCma/CanESM2/historical/day/atmos/day/r2i1p1/v20120410/tasmin/
    ....
    /g/data/al33/replicas/CMIP5/combined/NOAA-GFDL/GFDL-CM3/historical/day/atmos/day/r2i1p1/v20120227/tasmin/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/historical/day/atmos/day/r2i1p1/files/tasmin_20110518/
    
    Everything available on ESGF is also available locally


The tool first search on the ESGF for all the files that match the
constraints we passed. It then looks for these file locally and if it
finds them it returns their path on raijin. For all the files it can’t
find locally, the tool check an NCI table listing the downloads they are
working on. Finally it lists missing datasets which are in the download
queue, followed by the datasets that are not available locally and no
one has yet requested.

The tool list the datasets paths and dataset_ids, we used to have a
``--format file`` option but this has been removed in most recent
versions.

The query by default returns the latest available version. What if we
want to have a look at all the available versions?

.. code::

    !clef cmip5 --variable clivi --experiment historical --table Amon -m ACCESS1.0 --all-versions


.. parsed-literal::

    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/files/clivi_20120115/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/files/clivi_20120727/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r3i1p1/files/clivi_20140402/
    
    Everything available on ESGF is also available locally


The option ``--all-versions`` is the reverse of ``--latest``, which is
also the default, so we get a list of all available versions. Since all
the ACCESS1.0 data is available on NCI (which is the authoritative
source for the ACCESS models) the tool shouldn’t find any missing
datasets, if it does please let us know about it.

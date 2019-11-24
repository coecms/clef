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
to pass them as constraints in the same query:::

    !clef cmip5 -m CMCC-CM -e historical --experiment_family RCP -t Omon -v tos -en r1i1p1


    No matches found on ESGF, check at https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5&ensemble=r1i1p1&experiment=historical&model=CMCC-CM&cmor_table=Omon&variable=tos&experiment_family=RCP


We couldn’t find any matches because both constraints have to be true,
similarly if we pass rcp45 as experiment as well as the family RCP we
will only get the rcp45 results.::

    !clef cmip5 -m CMCC-CM -e rcp45 --experiment_family RCP -t Omon -v tos -en r1i1p1


    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20120518/tos/
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20170725/tos/
    
    Everything available on ESGF is also available locally


Finally, it is now possible to use experiment_family also in the local
search:::

    !clef --local cmip5 -m CMCC-CM --experiment_family RCP -t Omon -v tos -en r1i1p1


    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20120518/tos
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20170725/tos
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp85/mon/ocean/Omon/r1i1p1/v20120528/tos
    /g/data1b/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp85/mon/ocean/Omon/r1i1p1/v20170725/tos


Searching for other climate datasets: ds
----------------------------------------

Let’s get back to the command line now and have a look at the third
command **ds**\  This command let you query a separate database that
contains information on other climate datasets which are available on
raijin.::

    !clef ds --help


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
  database have been completed.::

    !clef ds


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
options to identify them is the best option.::

    !clef ds -f netcdf --standard-name air_temperature


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
is returned.::

    !clef ds -f netcdf --cmor-name ta


    T: /g/data/ub4/era5/netcdf/pressure/T/<year>/T_era5_-57 20 78 -140_<YYYYMMDD>_<YYYYMMDD>.nc
    T: /g/data/ub4/era5/netcdf/pressure/T/<year>/T_era5_-57 20 78 -140_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/1.0/ta/ta_6hr_ERAI_historical_oper_an_pl_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_ml/1.0/ta/ta_6hr_ERAI_historical_oper_an_ml_<YYYYMMDD>_<YYYYMMDD>.nc


This returns a subset of the previous query using the cmor_name to
clearly identify one kind of air_temperature.

Climate collections command line search
=======================================

The **ds** command is a new feature of clef and we are still defining its behaviour.
clef ds 
with no other argument will return a list of the local datasets available in the database.
NB this is not an exhaustive list of the climate collections at NCI and not all the datasets alredy in the database have been completed.::

    $ clef ds --help

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
        -va, --variable [T|U|V|Z]     Variable name as defined in files: tas, pr,
                                      sic, T ...
        --frequency [yr|mon|day|6hr|3hr|1hr]
                                      Time frequency on which variable is defined
        --from-date TEXT              To define a time range of availability of a
                                      variable, can be used on its own or
                                      together with to-date. Format is YYYYMMDD
        --to-date TEXT                To define a time range of availability of a
                                      variable, 
                                      can be used on its own or
                                      together with from-date. Format is YYYYMMDD
        --help                        Show this message and exit.

shows the available arguments, if you specify any of the variable options then the search will return a list of variables rather then datasets.
Since variables can be named differently among datasets, using the standard_nameor cmor_name options to identify them, if available, is the best option.

Examples
--------
::
    $ clef ds -f netcdf --standard-name air_temperature
      ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/1.0/ta/ta_6hr_ERAI_historical_oper_an_pl_<YYYYMMDD>_<YYYYMMDD>.nc
      tas: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_sfc/1.0/tas/tas_6hr_ERAI_historical_oper_an_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
      ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_ml/1.0/ta/ta_6hr_ERAI_historical_oper_an_ml_<YYYYMMDD>_<YYYYMMDD>.nc
      mn2t: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/mn2t/mn2t_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
      mx2t: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/mx2t/mx2t_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
      tas: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/tas/tas_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc

This returns all the variable available as netcdf files and with air_temperature as standard_name.
NB for each variable a path structure is returned.::

    $ clef ds -f netcdf --cmor-name ta
      ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/1.0/ta/ta_6hr_ERAI_historical_oper_an_pl_<YYYYMMDD>_<YYYYMMDD>.nc
      ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_ml/1.0/ta/ta_6hr_ERAI_historical_oper_an_ml_<YYYYMMDD>_<YYYYMMDD>.nc

This returns a subset of the previous search using the cmor_name to clearly identify one kind of air_temperature.

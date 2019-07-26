Getting Started
===============

CleF is presently installed in an anaconda environment, which must be
loaded before use (on either VDI or Raijin)::

    $ module use /g/data3/hh5/public/modules
    $ module load conda/analysis3-unstable
NB there is a clef version available on analysis3 but the one in unstable is more recent and has fixes for some bugs.

clef is accessed through the command-line `clef` program. There are
presently two main commands:

 * :code:`clef cmip5` to execute searches on the CMIP5 dataset

 * :code:`clef cmip6` to execute searches on the CMIP6 dataset

 * :code:`clef ds` to execute searches on non-ESGF climate datasets 

Examples
========

The search works like the ESGF search website, e.g. https://esgf.nci.org.au/search/esgf_nci.
Results can be filtered by using flags matching the ESGF search facets.

CMIP5
-----
::
    $ clef cmip5 --model ACCESS1.0 \
               --experiment historical \
               --frequency mon \
               --variable ua \
               --variable va

    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/v20120727/ua/
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/v20120727/va/
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r2i1p1/v20130726/ua/
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r2i1p1/v20130726/va/
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r3i1p1/v20140402/ua/
    /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r3i1p1/v20140402/va/

    Everything available on ESGF is also available locally

CMIP6
-----
::           
    $ clef cmip6 --activity CMIP \
               --experiment historical \
               --source_type AOGCM \
               --table Amon \
               --grid gr \
               --resolution "250 km" \
               --variable ua \
               --variable va

    /g/data1b/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/historical/r1i1p1f2/Amon/ua/gr/v20180917/
    /g/data1b/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/historical/r1i1p1f2/Amon/va/gr/v20180917/

    Available on ESGF but not locally:
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.historical.r2i1p1f2.Amon.ua.gr.v20181126
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.historical.r2i1p1f2.Amon.va.gr.v20181126

ds
--
::


    $ clef ds -f netcdf --standard-name air_temperature
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/1.0/ta/ta_6hr_ERAI_historical_oper_an_pl_<YYYYMMDD>_<YYYYMMDD>.nc
    tas: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_sfc/1.0/tas/tas_6hr_ERAI_historical_oper_an_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
    ta: /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_ml/1.0/ta/ta_6hr_ERAI_historical_oper_an_ml_<YYYYMMDD>_<YYYYMMDD>.nc
    mn2t: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/mn2t/mn2t_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
    mx2t: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/mx2t/mx2t_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc
    tas: /g/data/ub4/erai/netcdf/3hr/atmos/oper_fc_sfc/1.0/tas/tas_3hr_ERAI_historical_oper_fc_sfc_<YYYYMMDD>_<YYYYMMDD>.nc

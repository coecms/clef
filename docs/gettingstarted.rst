Getting Started
===============

CleF is presently installed in an anaconda environment under the hh5 project.
First you will need to get access to this project via https://my.nci.org.au/mancini/project/hh5.
Once you have confirmation of your membership, you will need to log out and log back into Gadi for the changes to take effect. 
If you have issues joining this project, please contact us at cws_help@nci.org.au.

Once you have access to hh5, you must load the anaconda environment before use (on either VDI or Gadi)::

    $ module use /g/data3/hh5/public/modules
    $ module load conda/analysis3-unstable
NB there is a clef version available on analysis3 but the one in unstable is more recent and has fixes for some bugs.

clef is accessed through the command-line `clef` program. There are
presently two main commands:

 * :code:`clef cmip5` to execute searches on the CMIP5 dataset

 * :code:`clef cmip6` to execute searches on the CMIP6 dataset

 * :code:`clef cordex` to execute searches on the CMIP6 dataset

 * :code:`clef ds` to execute searches on non-ESGF climate datasets 

Examples
--------

The search works like the ESGF search website, e.g. https://esgf.nci.org.au/search/esgf_nci.
Results can be filtered by using flags matching the ESGF search facets.

CMIP5
+++++
::

    $ clef cmip5 --model ACCESS1.0 \
               --experiment historical \
               --frequency mon \
               --variable ua \
               --variable va

    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/v20120727/ua/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/v20120727/va/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r2i1p1/v20130726/ua/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r2i1p1/v20130726/va/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r3i1p1/v20140402/ua/
    /g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r3i1p1/v20140402/va/

    Everything available on ESGF is also available locally

CMIP6
+++++
::           

    $ clef cmip6 --activity CMIP \
               --experiment historical \
               --source_type AOGCM \
               --table Amon \
               --grid gr \
               --resolution "250 km" \
               --variable ua \
               --variable va

    /g/data/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/historical/r1i1p1f2/Amon/ua/gr/v20180917/
    /g/data/oi10/replicas/CMIP6/CMIP/CNRM-CERFACS/CNRM-CM6-1/historical/r1i1p1f2/Amon/va/gr/v20180917/

    Available on ESGF but not locally:
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.historical.r2i1p1f2.Amon.ua.gr.v20181126
    CMIP6.CMIP.CNRM-CERFACS.CNRM-CM6-1.historical.r2i1p1f2.Amon.va.gr.v20181126


CORDEX
++++++
::

    $ clef cordex -dmod CSIRO-BOM-ACCESS1-3 -e historical -v tas -f mon
    /g/data/rr3/publications/CORDEX/output/AUS-44/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360J/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360K/v1/mon/tas/latest/
    /g/data/rr3/publications/CORDEX/output/AUS-44/UNSW/CSIRO-BOM-ACCESS1-3/historical/r1i1p1/UNSW-WRF360L/v1/mon/tas/latest/
    ...


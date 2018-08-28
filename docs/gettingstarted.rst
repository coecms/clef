Getting Started
===============

arccssive2 is presently installed in an anaconda environment, which must be
loaded before use (on either VDI or Raijin)::

    $ module use /g/data3/hh5/public/modules
    $ module load conda
    $ source activate arccssive2-test

arccssive2 is accessed through the command-line `esgf` program. There are
presently the following commands:

 * :code:`esgf [catalogue]` reports both local and missing files matching the given constraints

 * :code:`esgf --local [catalogue]` finds local files on NCI's ESGF mirror

 * :code:`esgf --missing [catalogue]` finds files on ESGF that haven't been downloaded to NCI

There are two catalogues that can be searched, :code:`cmip5` and :code:`cmip6`. The search terms used by each are
slightly different, you can see the list of terms by running e.g. :code:`esgf cmip5 --help`

The search works like the ESGF search website, e.g. https://esgf.nci.org.au/search/esgf_nci.
Results can be filtered by using flags::

    $ esgf --local cmip5 \
               --model ACCESS1.0 \
               --experiment historical \
               --time_frequency mon \
               --variable ua \
               --variable va

If the same flag is used multiple times both terms will be searched for. You
can also use :code:`%` as a wildcard, e.g. :code:`--model ACCESS%` to return
ACCESS1.0 and ACCESS1.3 data.

When querying the ESGF website, the total amount of results is limited to
1,000. If `arccssive2` finds more results it will ask you to refine your query.
You can follow the link to see the query `arccssive2` used on the ESGF
website::

    $ esgf --missing cmip5
    Exception: Too many results (1030069), try limiting your search
    https://esgf.nci.org.au/search/esgf_nci?query=&distrib=on&latest=on&project=CMIP5

Commands
========

esgf --missing
--------------

:code:`esgf --missing` searches ESGF for files that haven't been downloaded to
NCI. It returns ESGF file IDs for each missing file::

    $ esgf --missing cmip5 \
                   --model HadCM3 --experiment historical \
                   --time_frequency day --ensemble r1i1p1 \
                   --variable ta

    cmip5.output2.MOHC.HadCM3.historical.day.atmos.day.r1i1p1.v20110728.ta_day_HadCM3_historical_r1i1p1_18591201-18841130.nc|esgf-data1.ceda.ac.uk
    cmip5.output2.MOHC.HadCM3.historical.day.atmos.day.r1i1p1.v20110728.ta_day_HadCM3_historical_r1i1p1_18841201-19091130.nc|esgf-data1.ceda.ac.uk
    cmip5.output2.MOHC.HadCM3.historical.day.atmos.day.r1i1p1.v20110728.ta_day_HadCM3_historical_r1i1p1_19091201-19341130.nc|esgf-data1.ceda.ac.uk

NOTE: ESGF keeps track of only the most recent versions of each file, so if the
versions in the NCI mirror and ESGF don't match this command can return false
positives.

esgf --local
------------

:code:`esgf --local` searches the local file system for files that have been
downloaded to NCI. It returns the path to the file on NCI's /g/data disk::

     $ esgf --local cmip5 \
                  --model ACCESS1.0 --experiment historical \
                  --time_frequency day --ensemble r1i1p1 \
                  --variable ta --all-versions

     /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/day/atmos/day/r1i1p1/v20130124/ta/ta_day_ACCESS1-0_historical_r1i1p1_19500101-19541231.nc
     /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/day/atmos/day/r1i1p1/v20130124/ta/ta_day_ACCESS1-0_historical_r1i1p1_19550101-19591231.nc
     /g/data1/rr3/publications/CMIP5/output1/CSIRO-BOM/ACCESS1-0/historical/day/atmos/day/r1i1p1/v20130124/ta/ta_day_ACCESS1-0_historical_r1i1p1_19600101-19641231.nc

NOTE: Presently the default behaviour is to check for the most recent file
version on ESGF, and return only files with that version. This is likely to
change, and can be disabled with the :code:`--all-versions` flag.

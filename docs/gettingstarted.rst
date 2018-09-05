Getting Started
===============

CleF is presently installed in an anaconda environment, which must be
loaded before use (on either VDI or Raijin)::

    $ module use /g/data3/hh5/public/modules
    $ module load conda
    $ source activate clef-test

clef is accessed through the command-line `clef` program. There are
presently two main commands:

 * :code:`clef cmip5` to execute searches on the CMIP5 dataset

 * :code:`clef cmip6` to execute searches on the CMIP6 dataset

and four optional flags are available for each command to limit the output or submit a data request:

 * :code:`clef --remote cmip5` returns all the ESGF CMIP5/CMIP6 datasets  matching the constraints 

 * :code:`clef --local cmip5` finds local files on NCI's ESGF CMIP5/CMIP6  mirror

 * :code:`clef --missing cmip6` finds files on ESGF that haven't been downloaded to NCI

 * :code:`clef --request cmip6` create and pass to NCI a request to download the missing files
   (NB. this is not yet implemented!)

If these flags are omitted then the tool will search on the ESGF datasets matching the constraints and return both the local and missing files lists

The search works like the ESGF search website, e.g. https://esgf.nci.org.au/search/esgf_nci.
Results can be filtered by using flags matching the ESGF search facets::

    $ clef cmip5 --model ACCESS1.0 \
               --experiment historical \
               --frequency mon \
               --variable ua \
               --variable va

If the same flag is used multiple times both terms will be searched for. You
can also use :code:`%` as a wildcard, e.g. :code:`--model ACCESS%` to return
ACCESS1.0 and ACCESS1.3 data.

Please note that CMIP5 and CMIP6 have different names and number of flags, 
we tried to use the same names wherever possible.
In particular CMIP6 has some new flags available::
           
    $ clef cmip6 --activity CMIP \
               --experiment historical \
               --source_type AOGCM \
               --table Amon \
               --grid gr \
               --resolution "250 km" \
               --variable ua \
               --variable va

 `activity` - MIPS or sub-projects, for example CMIP refers to the DECK group of experiments
 `source_type` - model type in the example iabove AOGCM is coupled Atmosphere-Ocean Global Climate Model
 `grid` - grid kind, in the example 'gr' stands for "regridded data reported on the data provider's preferred target grid"
 `resolution` - nominal resolution of the grid, there are two kind of nominal resolution. 
             If the value is in degrees then this is a standard CMIP6 grid, currently only "1x1 degree" is available.
             If the resolution is in kms then this is an approximate resolution. Details are available in the appendix 2 of the CMIP6 attributes documentation:  https://goo.gl/v1drZl
             Note that resolution is always composed of two separate words and will need to be passed as a string enclosed in quotes "". 

When querying the ESGF website, the total amount of results is limited to
1,000. If `clef` finds more results it will ask you to refine your query.
You can follow the link to see the query `clef` used on the ESGF
website::

    $ clef cmip5
    Exception: Too many results (1030069), try limiting your search
    https://esgf.nci.org.au/search/esgf_nci?query=&distrib=on&latest=on&project=CMIP5

Options
========

clef --missing
------------

:code:`clef --missing <dataset>` searches ESGF for files that haven't been downloaded to
NCI. It returns ESGF dataset IDs for each dataset that has one or more missing files::

    $ clef --missing cmip5 --model HadCM3 --experiment historical \
                   --table day --ensemble r1i1p1 \
                   --variable ta
    Available on ESGF but not locally:
    cmip5.output2.MOHC.HadCM3.historical.day.atmos.day.r1i1p1.v20110728

NOTE: ESGF keeps track of only the most recent versions of each file for a given dataset version,
 so if the files in the NCI mirror and ESGF don't match this command can return false positives.

clef --local
----------

:code:`clef --local <dataset>` searches the local file system for files that have been
downloaded to NCI. It returns the path to the file on NCI's /g/data disk::

     $ clef --local cmip5 --model HadCM3 --experiment historical --table day --ensemble r1i1p1 \
                          --variable ta --all-versions
     /g/data1/ua6/unofficial-ESG-replica/tmp/tree/cmip-dn1.badc.rl.ac.uk/thredds/fileServer/esg_dataroot/cmip5/output1/MOHC/HadCM3/historical/day/atmos/day/r1i1p1/v20110728/ta/
     /g/data1/ua6/unofficial-ESG-replica/tmp/tree/esgf-data1.ceda.ac.uk/thredds/fileServer/esg_dataroot/cmip5/output1/MOHC/HadCM3/historical/day/atmos/day/r1i1p1/v20140110/ta/


NOTE: Presently the default behaviour is to check for the most recent (latest) version
on ESGF, and return only files with that version. This can be disabled with the :code:`--all-versions` flag.
If a version has been unpublished by the ESGF but it is still available locally,
 even using the `--all-versions` flag this won't appear in the results. We are working on a solution for this.
If you are sure a version should exists only for CMIP5 you could try using the ARCCSSive module https://github.com/coecms/arccssive to locate it.

tips
--------

If your search doesn't return any results try again at a later time. The tool is searching the ESGF website first 
and sometimes one or more nodes can be disconnected and the returned results are incomplete.
This shouldn't be anymore an issue once we implemented a search for files which are locally available but not published yet.
As in that case for CMIP5 you can use the older ARCCSSive tool if in doubt.

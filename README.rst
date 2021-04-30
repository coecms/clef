=============================
𝄞 `clef <https://clef.readthedocs.io/en/stable>`_
=============================

CleF - Climate Finder - Dataset search tool developed by the `CLEX <https://climateextremes.org.au>`_ `CMS <https://climate-cms.org>`_ team, powered by `ESGF <https://esgf-node.llnl.gov/>`_ and the `NCI <https://nci.org.au>`_ clef.nci.org.au local database

.. image:: https://readthedocs.org/projects/clef/badge/?version=latest
  :target: https://clef.readthedocs.io/en/stable/
.. image:: https://circleci.com/gh/coecms/clef/tree/master.svg?style=shield
  :target: https://circleci.com/gh/coecms/clef/tree/master
.. image:: https://api.codacy.com/project/badge/Grade/aabc5bed0d284dc3970d32e5ecbfe460
  :target: https://www.codacy.com/app/ScottWales/clef
.. image:: https://api.codacy.com/project/badge/Coverage/aabc5bed0d284dc3970d32e5ecbfe460
  :target: https://www.codacy.com/app/ScottWales/clef
.. image:: https://img.shields.io/conda/v/coecms/clef.svg
  :target: https://anaconda.org/coecms/clef
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4729030.svg
   :target: https://doi.org/10.5281/zenodo.4729030

.. content-marker-for-sphinx

Clef searches the Earth System Grid Federation datasets stored at the Australian National Computational Infrastructure, both data published on the NCI
ESGF node as well as files that are locally replicated from other ESGF nodes.

Currently it searches for the following datasets:

- **CMIP5**  raijin projects: rr3, where NCI is the primary publisher and al33 for replicas 
- **CMIP6**  raijin projects: 0i10 for replicas 
- **CORDEX**  raijin projects: rr3, where NCI is the primary publisher and al33 for replicas 

The search returns both the path of data that is already available at NCI as well as information on data that
is on external ESGF nodes but not yet available locally.

-------
Install
-------

Clef is pre-installed into a Conda environment at NCI. Load it with::

    module use /g/data3/hh5/public/modules
    module load conda/analysis3-unstable

NB You need to be a member of hh5 to load the modules

We are constantly adding new features, the development version is available in a separate environment::
    module use /g/data3/hh5/public/modules
    module load conda
    source activate clef-test

You can install it to your own environment with::

    conda install -c coecms -c conda-forge clef

But note that the clef.nci.org.au database necessary for running ``clef`` can only be accessed
from NCI systems

---
Use
---

clef cmip5
~~~~~

Find CMIP5 files matching the constraints::

    clef cmip5 --model BCC-CSM1.1 --variable tas --experiment historical --table day

You can filter CMIP5 by the following terms:
 
 * ensemble/member
 * experiment
 * experiment-family
 * model
 * table/cmor_table
 * realm
 * frequency
 * variable
 * cf-standard-name
 * institution

See ``clef cmip5 --help`` for all available filters and their aliases

   ``--latest`` will check the latest versions of the datasets on the ESGF
website, and will only return matching files

It will return a path for all the files available locally at NCI and a dataset-id for the ones that haven't been downloaded yet.

You can use the flags ``--local`` and ``--missing`` to return respectively only the local paths or the missing dataset-id::

    clef --local cmip5 --model MPI-ESM-LR --variable tas --table day
    clef --missing cmip5 --model MPI-ESM-LR --variable tas --table day

NB these flags come immediately after the command "clef" and before the sub-command "cmip5" or "cmip6". They are also clearly mutually exclusive.
You can repeat arguments more than once:: 

    clef --missing cmip5 --model MPI-ESM-LR -v tas -v tasmax -t day -t Amon

clef cmip6
~~~~~

You can filter CMIP6 by the following terms:
 
 * activity
 * experiment
 * source_type 
 * model
 * member
 * table
 * grid
 * resolution
 * realm
 * frequency
 * variable
 * version
 * sub_experiment
 * variant_label
 * institution
 * cf_standard_name

See ``clef cmip6 --help`` for all available filters

clef cordex
~~~~~

You can filter CORDEX by the following terms:
 
 * experiment
 * domain
 * driving_model
 * rcm_name (model)
 * rcm_version
 * ensemble
 * table
 * time_frequency
 * variable
 * version
 * experiment_family
 * institute
 * cf_standard_name

See ``clef cordex --help`` for all available filters

-------
-------
Develop
-------

Development install::

    conda env create -f conda/dev-environment.yml
    source activate clef-dev
    pip install -e '.[dev]'

The `dev-environment.yml` file is for speeding up installs and installing
packages unavailable on pypi, `requirements.txt` is the source of truth for
dependencies.

To work on the database tables you may need to start up a test database.

You can start a test database either with Docker::

    docker-compose up # (In a separate terminal)
    psql -h localhost -U postgres -f db/nci.sql
    psql -h localhost -U postgres -f db/tables.sql
    # ... do testing
    docker-compose rm

Or with Vagrant::

    vagrant up
    # ... do testing
    vagrant destroy

Run tests with py.test (they will default to using the test database)::

    py.test

or connect to the production database with::

    py.test --db=postgresql://clef.nci.org.au/postgres

Build the documentation using Sphinx::

    python setup.py build_sphinx
    firefox docs/_build/index.html

New releases are packaged and uploaded to anaconda.org by CircleCI when a new
Github release is made

Documentation is available on ReadTheDocs, both for `stable
<https://clef.readthedocs.io/en/stable/>`_ and `latest
<https://clef.readthedocs.io/en/latest/>`_ versions.

Disclaimer
----------
CleF can only return datasets which are listed in the ESGF database system for remote results and on the NCI clef database for local results. This means that potentially some of the datasets might not be returned in the following cases:
 * One or more of the ESGF nodes are offline: this can affect clef returning results for the models which are hostedworks which are offline. It is usually easy to verify if this is the case since a query on the browser should show a reduced list of models. In such cases using the *--local* flag will use a query method completely independent and will return at least what is available locally.
 * The NCI ESGF node is offline then nothing will be returned by the default or remote queries, again using *--local* should work. 
 * The checksums stored in the ESGF database are different from the actual file checksums. CleF uses the checksums to match the files available remotely if even one file does not match it will flag the dataset as missing. Using the *--local* flag should still return the datasets regardless because it doesn't compare them to what is available remotely. 
 * A dataset has been recently donwloaded (up to a week before) and hasn't yet been added to the NCI clef database. In such case it might not show locally even if it has been downloaded. The NCI clef database is updated weekly so we cannot guarantee for clef to find data which is more recent than that. NCI also provides us with a list of datasets recently queued or downloaded. The default query will show this data as "queued" or "downloaded", rather than missing. While this list aims to cover the gap in between database updates, we have no control on its frequency and it might not capture all the data.

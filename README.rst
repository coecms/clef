=============================
𝄞 `clef <https://clef.readthedocs.io/en/stable>`_
=============================

CleF - Climate Finder - Dataset search tool developed by the `CLEX <https://climateextremes.org.au>`_ `CMS <https://climate-cms.org>`_ team, powered by `ESGF <https://esgf-node.llnl.gov/>`_ and the `NCI <https://nci.org.au>`_ MAS database

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

.. content-marker-for-sphinx

Clef searches the Earth System Grid Federation datasets stored at the Australian National Computational Infrastructure, both data published on the NCI
ESGF node as well as files that are locally replicated from other ESGF nodes.

Currently it searches the following datasets:

- **rr3** NCI published data
- **al33** CMIP5 replicas
- **oi10** CMIP6 replicas

It can report both datasets that are available at NCI as well as datasets that
are on external ESGF nodes but not available at NCI

-------
Install
-------

Clef is pre-installed into a Conda environment at NCI. Load it with::

    module use /g/data3/hh5/public/modules
    module load conda
    source activate clef-test

You can install it to your own environment with::

    conda install -c coecms -c conda-forge clef

But note that the MAS database necessary for running ``clef`` can only be accessed
from NCI systems

---
Use
---

Find CMIP5 files matching the constraints::

    clef cmip5 --model BCC-CSM1.1 --variable tas --experiment historical --table day

You can filter CMIP5 by the following terms:
 
 * ensemble/member
 * experiment
 * experiment-family
 * institution
 * model
 * table/cmor_table
 * realm
 * frequency
 * variable
 * cf-standard-name

See ``clef cmip5 --help`` for all available filters and their aliases

   ``--latest`` will check the latest versions of the datasets on the ESGF
website, and will only return matching files

It will return a path for all the files available locally at NCI and a dataset-id for the ones that haven't been downloaded yet.

You can use the flags ``--local`` and ``--missing`` to return respectively only the local paths or the missing dataset-id::

    clef --local cmip5 --model MPI-ESM-LR --variable tas --table day
    clef --missing cmip5 --model MPI-ESM-LR --variable tas --table day

You can repeat arguments more than once:: 

    clef --missing cmip5 --model MPI-ESM-LR -v tas -v tasmax -t day -t Amon

You can filter CMIP6 by the following terms:
 
 * activity
 * experiment
 * institution
 * source_type 
 * model
 * member
 * table
 * realm
 * frequency
 * variable
 * version

See ``clef cmip6 --help`` for all available filters

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

Build the documentation using Sphinx::

    python setup.py build_sphinx
    firefox docs/_build/index.html

New releases are packaged and uploaded to anaconda.org by CircleCI when a new
Github release is made

Documentation is available on ReadTheDocs, both for `stable <https://clef.readthedocs.io/en/stable/>`_ and `latest <https://clef.readthedocs.io/en/latest/>`_ versions.

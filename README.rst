=============================
clef
=============================

NCI ESGF Replica Search - Developed by the CLEX CMS team, powered by ESGF and the NCI MAS database

.. image:: https://readthedocs.org/projects/clef/badge/?version=stable
  :target: https://readthedocs.org/projects/clef/?badge=stable
.. image:: https://circleci.com/gh/coecms/clef/tree/master.svg?style=shield
  :target: https://circleci.com/gh/coecms/clef/tree/master
.. image:: https://api.codacy.com/project/badge/Grade/aabc5bed0d284dc3970d32e5ecbfe460
  :target: https://www.codacy.com/app/ScottWales/clef
.. image:: https://api.codacy.com/project/badge/Coverage/aabc5bed0d284dc3970d32e5ecbfe460
  :target: https://www.codacy.com/app/ScottWales/clef
.. image:: https://img.shields.io/conda/v/coecms/clef.svg
  :target: https://anaconda.org/coecms/clef

.. content-marker-for-sphinx

-------
Install
-------

Conda install::

    conda install -c coecms -c conda-forge clef

---
Use
---

Find CMIP5 files matching the constraints::

    clef cmip5 --model mpi% --variable tas --experiment historical --table day

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

``%`` acts as a wildcard character

``--latest`` will check the latest versions of the datasets on the ESGF
website, and will only return matching files

It will return a path for all the files available locally at NCI and a dataset-id for the ones that haven't been downloaded yet

You can use the flags ``--local`` and ``--missing`` to return respectively only the local paths or the missing dataset-id::

    clef --local cmip5 --model MPI-ESM-LR --variable tas --table day
    clef --missing cmip5 --model MPI-ESM-LR --variable tas --table day

You can repeat arguments more than once 

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

Start test DB (optional, requires Docker)::
    docker-compose up # (In a separate terminal)
    psql -h localhost -U postgres -f db/nci.sql
    psql -h localhost -U postgres -f db/tables.sql

Run tests::

    py.test

Build documentation::

    python setup.py build_sphinx
    firefox docs/_build/index.html

Upload documentation::

    git subtree push --prefix docs/_build/html/ origin gh-pages

New releases are packaged and uploaded to anaconda.org by CircleCI when a new
Github release is made

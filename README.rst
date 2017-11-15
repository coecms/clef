=============================
arccssive2
=============================

arccssive2

.. image:: https://readthedocs.org/projects/arccssive2/badge/?version=latest
  :target: https://readthedocs.org/projects/arccssive2/?badge=latest
.. image:: https://travis-ci.org/coecms/arccssive2.svg?branch=master
  :target: https://travis-ci.org/coecms/arccssive2
.. image:: https://circleci.com/gh/coecms/arccssive2.svg?style=shield
  :target: https://circleci.com/gh/coecms/arccssive2
.. image:: http://codecov.io/github/coecms/arccssive2/coverage.svg?branch=master
  :target: http://codecov.io/github/coecms/arccssive2?branch=master
.. image:: https://landscape.io/github/coecms/arccssive2/master/landscape.svg?style=flat
  :target: https://landscape.io/github/coecms/arccssive2/master
.. image:: https://codeclimate.com/github/coecms/arccssive2/badges/gpa.svg
  :target: https://codeclimate.com/github/coecms/arccssive2
.. image:: https://badge.fury.io/py/arccssive2.svg
  :target: https://pypi.python.org/pypi/arccssive2

.. content-marker-for-sphinx

-------
Install
-------

Conda install::

    conda install -c coecms arccssive2

Pip install (into a virtual environment)::

    pip install arccssive2

---
Use
---

Find files at NCI downloaded from ESGF::

    esgf local --model mpi% --variable tas --experiment historical --time_frequency=day

You can filter by the following terms:
 
 * ensemble
 * experiment
 * institute
 * model
 * project
 * realm
 * time_frequency
 * variable
 * version

``%`` acts as a wildcard character

``--latest`` will check the latest versions of the datasets on the ESGF
website, and will only return matching files

Find files on ESGF that haven't been downloaded to NCI (note wildcards don't work)::

    esgf missing --model MPI-ESM-LR --variable tas --time_frequency=day

Any normal arguments will be passed into the ESGF search, though this may have
false positives::

    esgf missing MPI-ESM-LR tas day

See ``esgf missing --help`` for all available filters

---
Saving your password
---

To save/update your password, run::

    keyring set arccssive2 $USER

This will save your NCI password into the system keyring

-------
Develop
-------

Development install::

    conda env create -f conda/dev-environment.yml
    source activate arccssive2-dev
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

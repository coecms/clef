CSV file output
~~~~~~~~~~~~~~~

The *–csv* option added to the command line will output the query
results in a csv file. rather than getting only the files path, it will
list all the available attributes. This currently works only with the
*–local* option, it doesn’t yet work for the standard search or remote.
These last both perform an ESGF query rather than searching directly the
MAS database as *local* so they need to be treated differently. We are
still working on this.

.. code:: ipython3

    clef --local cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id --csv

.. code:: ipython3

    head -n 4 CMIP6_query.csv

Query summary option
~~~~~~~~~~~~~~~~~~~~

The *–stats* option added to the command line will print a summary of
the query results Currently it prints the following: \* total number of
models, followed by their names \* total number of unique
model-ensembles/members combinations \* number of models that have N
ensembles/members, followed by their names

.. code:: ipython3

    clef --local cmip5 -v pr -v mrso -e piControl --frequency mon --stats

Searching for other climate datasets: ds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The third clef sub-command **ds** let you query a separate database that
contains information on other climate datasets which are available on
raijin.

.. code:: ipython3

    clef ds --help

| clef ds
| with no other argument will return a list of the local datasets
  available in the database. NB this is not an exhaustive list of the
  climate collections at NCI and not all the datasets already in the
  database have been completed.

.. code:: ipython3

    clef ds

If you specify any of the variable options then the query will return a
list of variables rather then datasets. Since variables can be named
differently among datasets, using the *standard_name* or *cmor_name* 
options to identify them is the best option.

.. code:: ipython3

    clef ds -f netcdf --standard-name air_temperature

This returns all the variable available as netcdf files and with
air_temperature as standard_name.
NB for each variable a path structure is returned.

.. code:: ipython3

    clef ds -f netcdf --cmor-name ta

This returns a subset of the previous query using the cmor_name to
clearly identify one kind of air_temperature.

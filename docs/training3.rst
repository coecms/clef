
Integrating the local query in your scripts
-------------------------------------------

Until now we looked at how to run queries from the command line, but you
can use use the same query run by the *–local* option directly in your
python code. By doing so you also get access to a lot more information
on the datasets returned not only the path. To do so we have first to
import some functions from the clef.code sub-module. In particular the
**search()** function and **connect()** and **Session()** that we’ll use
to open a connection to the database.

.. code:: ipython3

    from clef.code import *
    db = connect()
    s = Session()

Running search()
~~~~~~~~~~~~~~~~

**search()** takes 4 inputs: the db session, the project (i.e. currently
‘cmip5’ or ‘cmip6’), latest (True or False) and a dictionary containing
the query constraints: > search(session, project=‘CMIP5’, latest=True,
\**kwargs)

Let’s start by defining some constraints.

.. code:: ipython3

    constraints = {'variable': 'tas', 'model': 'MIROC5', 'cmor_table': 'day', 'experiment': 'rcp85'}

The available keys depend on the project you are querying and the
attributes stored by the database. You can use any of the *facets* used
for ESGF but in future we will be adding other options based on extra
fields which are stored as attributes.

.. code:: ipython3

    results = search(s, project='CMIP5', **constraints)
    results




.. parsed-literal::

    [{'filenames': ['tas_day_MIROC5_rcp85_r1i1p1_20100101-20191231.nc',
       'tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231.nc',
       ...
       'tas_day_MIROC5_rcp85_r1i1p1_20200101-20291231.nc'],
      'project': 'CMIP5',
      'institute': 'MIROC',
      'model': 'MIROC5',
      'experiment': 'rcp85',
      'frequency': 'day',
      'realm': 'atmos',
      'r': '1',
      'i': '1',
      'p': '1',
      'ensemble': 'r1i1p1',
      'cmor_table': 'day',
      'version': '20120710',
      'variable': 'tas',
      'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas',
      'periods': [('20100101', '20191231'),
       ...
       ('20200101', '20291231')],
      'fdate': '20060101',
      'tdate': '21001231',
      'time_complete': True},
     {'filenames': ['tas_day_MIROC5_rcp85_r2i1p1_20900101-20991231.nc',
       ...},
       ...]

Both the keys and values of the constraints get checked before being
passed to the query function. This means that if you passed a key or a
value that doesn’t exist for the chosen project, the function will print
a list of valid values and then exit. Let’s re-write the constraints
dictionary to show an example.

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'activity': 'CMIP'}
    results = search(s, **constraints)


::


    ---------------------------------------------------------------------------

    ClefException: Warning activity is not a valid constraint nameValid constraints are:
    dict_values([['source_id', 'model', 'm'], ['realm'], ['time_frequency', 'frequency', 'f'], ['variable_id', 'variable', 'v'], ['experiment_id', 'experiment', 'e'], ['table_id', 'table', 'cmor_table', 't'], ['member_id', 'member', 'ensemble', 'en', 'mi'], ['institution_id', 'institution', 'institute'], ['experiment_family']])


You can see that the function told us ‘activity’ is not a valid
constraints for CMIP5, in fact that can be used only with CMIP6 NB. that
the search accepted all the other abbreviations, there’s a few terms
that can be used for each key. The full list of valid keys is available
from from the github repository:
https://github.com/coecms/clef/blob/master/clef/data/valid_keys.json

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'member': 'r1i1p1'}
    results = search(s, **constraints)
    results[0]



.. parsed-literal::

    {'filenames': ['tas_day_MIROC5_rcp85_r1i1p1_20100101-20191231.nc',
      'tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231.nc',
      ...
      'tas_day_MIROC5_rcp85_r1i1p1_20200101-20291231.nc'],
     'project': 'CMIP5',
     'institute': 'MIROC',
     'model': 'MIROC5',
     'experiment': 'rcp85',
     'frequency': 'day',
     'realm': 'atmos',
     'r': '1',
     'i': '1',
     'p': '1',
     'ensemble': 'r1i1p1',
     'cmor_table': 'day',
     'version': '20120710',
     'variable': 'tas',
     'pdir': '/g/data1b/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas',
     'periods': [('20100101', '20191231'),
      ('20900101', '20991231'),
      ...
      ('20200101', '20291231')],
     'fdate': '20060101',
     'tdate': '21001231',
     'time_complete': True}



NB that *project* is by default ‘CMIP5’ so it can be omitted when
querying CMIP5 data and *latest* is True by default. Set this to *False*
if you want to return all the available versions.

Running search() for different sets of attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The **search()** function works for one set of attributes, you can
specify only one value for each of the attributes at one time. If you
want to run a query for two or more different sets of attributes you can
call **search()** in a loop. If you have a small numbers of queries then
this is easy to implement and run. To make **search()** works for a
random number of inputs passed by the command line we set up a function
**call_local_query()** that deals with this more efficiently. The
arguments are very similar to **search()** with the important difference
that we are passing list of values instead of strings:
>call_local_query(s, project, oformat, latest, \**kwargs)

Let’s look at an example:

.. code:: ipython3

    constraints = {'variable': ['tasmin','tasmax'], 'model': ['MIROC5','MIROC4h'],
                   'cmor_table': ['day'], 'experiment': ['rcp85'], 'ensemble': ['r1i1p1']}
    results, paths = call_local_query(s, project='CMIP5', oformat='Dataset', latest=True, **constraints)

Because this function was created to deliver results for the command
line local query option, as well as the list of results, it also outputs
a list of their paths. Under the hood this function works out all the
combinations of the arguments you passed and will run **search()** for
each of them, before doing so will also run other functions that check
that the values and keys passed to the function are valid. The extra
arguments *oformat* and “latest” are necessary to resolve the command
line *–format* and *–latest* option respectively. The first can be
‘file’ or ‘dataset’, with the last being the default. It influences the
*paths* output but no *results* which will contain all the datasets
information including filenames.

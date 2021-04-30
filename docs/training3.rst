Integrating the local query in your scripts
-------------------------------------------

Until now we looked at how to run queries from the command line, but you
can use use the same query run by the ``--local`` option directly in
your python code. By doing so you also get access to a lot more
information on the datasets returned not only the path. To do so we have
first to import some functions from the clef.code sub-module. In
particular the **search( )** function and **connect( )** and **Session(
)** that we’ll use to open a connection to the database.

.. code:: ipython3

    from clef.code import *
    db = connect()
    s = Session()

Running search( )
~~~~~~~~~~~~~~~~~

**search( )** takes 4 inputs: the db session, the project
(i.e. currently ‘CMIP5’, ‘CORDEX’ or ‘CMIP6’), latest (True or False)
and a dictionary containing the query constraints: > search(session,
project=‘CMIP5’, latest=True, \**kwargs)

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

.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>project</th>
          <th>institute</th>
          <th>model</th>
          <th>experiment</th>
          <th>frequency</th>
          <th>realm</th>
          <th>ensemble</th>
          <th>cmor_table</th>
          <th>version</th>
          <th>variable</th>
          <th>path</th>
          <th>filename</th>
          <th>periods</th>
          <th>fdate</th>
          <th>tdate</th>
          <th>time_complete</th>
        </tr>
        <tr>
          <th>path</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>/g/data/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas</th>
          <td>CMIP5</td>
          <td>MIROC</td>
          <td>MIROC5</td>
          <td>rcp85</td>
          <td>day</td>
          <td>atmos</td>
          <td>r1i1p1</td>
          <td>day</td>
          <td>20120710</td>
          <td>tas</td>
          <td>/g/data/al33/replicas/CMIP5/combined/MIROC/MIR...</td>
          <td>{tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231...</td>
          <td>[(21000101, 21001231), (20800101, 20891231), (...</td>
          <td>20060101</td>
          <td>21001231</td>
          <td>True</td>
        </tr>
        <tr>
          <th>/g/data/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r2i1p1/v20120710/tas</th>
          <td>CMIP5</td>
          <td>MIROC</td>
          <td>MIROC5</td>
          <td>rcp85</td>
          <td>day</td>
          <td>atmos</td>
          <td>r2i1p1</td>
          <td>day</td>
          <td>20120710</td>
          <td>tas</td>
          <td>/g/data/al33/replicas/CMIP5/combined/MIROC/MIR...</td>
          <td>{tas_day_MIROC5_rcp85_r2i1p1_20600101-20691231...</td>
          <td>[(21000101, 21001231), (20800101, 20891231), (...</td>
          <td>20060101</td>
          <td>21001231</td>
          <td>True</td>
        </tr>
        <tr>
          <th>/g/data/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r3i1p1/v20120710/tas</th>
          <td>CMIP5</td>
          <td>MIROC</td>
          <td>MIROC5</td>
          <td>rcp85</td>
          <td>day</td>
          <td>atmos</td>
          <td>r3i1p1</td>
          <td>day</td>
          <td>20120710</td>
          <td>tas</td>
          <td>/g/data/al33/replicas/CMIP5/combined/MIROC/MIR...</td>
          <td>{tas_day_MIROC5_rcp85_r3i1p1_20300101-20391231...</td>
          <td>[(21000101, 21001231), (20800101, 20891231), (...</td>
          <td>20060101</td>
          <td>21001231</td>
          <td>True</td>
        </tr>
        <tr>
          <th>/g/data/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r4i1p1/v20131009/tas</th>
          <td>CMIP5</td>
          <td>MIROC</td>
          <td>MIROC5</td>
          <td>rcp85</td>
          <td>day</td>
          <td>atmos</td>
          <td>r4i1p1</td>
          <td>day</td>
          <td>20131009</td>
          <td>tas</td>
          <td>/g/data/al33/replicas/CMIP5/combined/MIROC/MIR...</td>
          <td>{tas_day_MIROC5_rcp85_r4i1p1_20300101-20351231...</td>
          <td>[(20060101, 20091231), (20200101, 20291231), (...</td>
          <td>20060101</td>
          <td>20351231</td>
          <td>True</td>
        </tr>
        <tr>
          <th>/g/data/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r5i1p1/v20131009/tas</th>
          <td>CMIP5</td>
          <td>MIROC</td>
          <td>MIROC5</td>
          <td>rcp85</td>
          <td>day</td>
          <td>atmos</td>
          <td>r5i1p1</td>
          <td>day</td>
          <td>20131009</td>
          <td>tas</td>
          <td>/g/data/al33/replicas/CMIP5/combined/MIROC/MIR...</td>
          <td>{tas_day_MIROC5_rcp85_r5i1p1_20300101-20351231...</td>
          <td>[(20060101, 20091231), (20200101, 20291231), (...</td>
          <td>20060101</td>
          <td>20351231</td>
          <td>True</td>
        </tr>
      </tbody>
    </table>
    </div>



The **search( )** function returns a pandas dataframe where every match
to the constraints is a row.

Both the keys and values of the constraints get checked before being
passed to the query function. This means that if you passed a key or a
value that doesn’t exist for the chosen project, the function will print
a list of valid values and then exit. Let’s rewrite the constraints
dictionary to show an example.

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'activity': 'CMIP'}
    results = search(s, **constraints)


::


    ---------------------------------------------------------------------------

    ClefException                             Traceback (most recent call last)

    <ipython-input-20-c5717342465f> in <module>
          1 constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'activity': 'CMIP'}
    ----> 2 results = search(s, **constraints)
    

    ~/.local/lib/python3.8/site-packages/clef/code.py in search(session, project, latest, **kwargs)
         61     valid_keys = get_keys(project)
         62     # check all passed keys are valid
    ---> 63     args = check_keys(valid_keys, kwargs)
         64     # load dictionary of valid keys for project facets
         65     vocabularies = load_vocabularies(project)


    ~/.local/lib/python3.8/site-packages/clef/helpers.py in check_keys(valid_keys, kwargs)
        208         facets = [k for k,v in valid_keys.items() if key in v]
        209         if facets==[]:
    --> 210             raise ClefException(
        211                 f"Warning {key} is not a valid constraint name"
        212                 f"Valid constraints are:\n{valid_keys.values()}")


    ClefException: Warning activity is not a valid constraint nameValid constraints are:
    dict_values([['source_id', 'model', 'm'], ['realm'], ['time_frequency', 'frequency', 'f'], ['variable_id', 'variable', 'v'], ['experiment_id', 'experiment', 'e'], ['table_id', 'table', 'cmor_table', 't'], ['member_id', 'member', 'ensemble', 'en', 'mi'], ['institution_id', 'institution', 'institute'], ['experiment_family'], ['cf_standard_name']])


You can see that the function told us ``activity`` is not a valid
constraints for CMIP5, in fact that can be used only with CMIP6 NB. that
the search accepted all the other abbreviations, there’s a few terms
that can be used for each key. The full list of valid keys is available
from from the github repository:
https://github.com/coecms/clef/blob/master/clef/data/valid_keys.json

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'member': 'r1i1p1'}
    results = search(s, **constraints)
    results.iloc[0,:]


.. parsed-literal::

    project                                                      CMIP5
    institute                                                    MIROC
    model                                                       MIROC5
    experiment                                                   rcp85
    frequency                                                      day
    realm                                                        atmos
    ensemble                                                    r1i1p1
    cmor_table                                                     day
    version                                                   20120710
    variable                                                       tas
    path             /g/data/al33/replicas/CMIP5/combined/MIROC/MIR...
    filename         {tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231...
    periods          [(21000101, 21001231), (20800101, 20891231), (...
    fdate                                                     20060101
    tdate                                                     21001231
    time_complete                                                 True
    Name: /g/data/al33/replicas/CMIP5/combined/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas, dtype: object



NB that ``project`` is by default ‘CMIP5’ so it can be omitted when
querying CMIP5 data and ``latest`` is True by default. Set this to
*False* if you want to return all the available versions.

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
    results, paths = call_local_query(s, project='CMIP5', latest=True, **constraints)

Because this function was created to deliver results for the command
line local query option, as well as the list of results, it also outputs
a list of their paths. Under the hood this function works out all the
combinations of the arguments you passed and will run **search()** for
each of them, before doing so will also run other functions that check
that the values and keys passed to the function are valid. The extra
argument ``latest`` is necessary to resolve the command line
``--latest`` option.

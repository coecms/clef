Using CleF queries  directly in your code
=========================================

The **code** sub-module contains functions which are used to run *--local* option and can be used to integrate this query in your own python scripts:: 

    from clef.code import *

After importing them you need to open a connection with the NCI local database to be able to run your queries::

    db = connect()
    s = Session()

The **search** function takes 4 inputs: the db session, the project (currently 'CMIP5' or 'CMIP6'), latest (True or False) and a dictionary containing the query constraints::

    df = search(s, project='CMIP5', latest=True, **constraints)

The keys available to define your constraints depend on the project you are querying and the attributes stored by the database. You can use any of the *facets* used for ESGF but in future we will be adding other options based on extra fields which are stored as attributes.  

Examples
--------
Here we defined the input dictionary for a CMIP5 query and print out the results dataframe::

    constraints = {'variable': 'tas', 'model': 'MIROC5', 'cmor_table': 'day', 'experiment': 'rcp85'}
    df = search(s, project='CMIP5', **constraints)
    df
    /g/data/al33/replicas/CMIP5/combined/MIROC/MIRO...   CMIP5  ...  [tas_day_MIROC5_rcp85_r1i1p1_20060101-20091231...
    /g/data/al33/replicas/CMIP5/combined/MIROC/MIRO...   CMIP5  ...  [tas_day_MIROC5_rcp85_r2i1p1_20060101-20091231...
    /g/data/al33/replicas/CMIP5/combined/MIROC/MIRO...   CMIP5  ...  [tas_day_MIROC5_rcp85_r3i1p1_20060101-20091231...

    [5 rows x 12 columns]
    'project', 'institute', 'model', 'experiment', 'frequency', 'realm', 'ensemble', 'cmor_table', 'version', 'variable', 'path', 'filename'

**search** returns a pandas dataframe, one row for each dataset.

Both the keys and values of the constraints get checked before being passed to the query function. This means that if you passed a key or a value that does not exist for the chosen project, the function will print a list of valid values and then exit.
Let's change the constraints dictionary to show an example::

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'e': 'rcp85', 'activity':'CMIP'}
    df = search(s, project='cmip5', **constraints)
    Warning activity is not a valid constraint name
    Valid constraints are:
    dict_values([['source_id', 'model', 'm'], ['realm'], ['time_frequency', 'frequency', 'f'], ['variable_id', 'variable', 'v'], ['experiment_id', 'experiment', 'e'], ['table_id', 'table', 'cmor_table', 't'], ['member_id', 'member', 'ensemble', 'en', 'mi'], ['institution_id', 'institution', 'institute'], ['experiment_family']])

You can see that the function told us 'activity' is not a valid constraints for CMIP5, in fact that can be used only with CMIP6
We used a shorter version for the keys, we allowed more than one term to be used for each key. The full list is available from the github repository:
https://github.com/coecms/clef/blob/master/clef/data/valid_keys.json

More examples and a full description of the function are available in the training page.

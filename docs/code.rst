Integrating the ESGF search in your code
========================================

The **code** sub-module contains functions which are used to run *--local* option and can be used to integrate this query in your own python scripts:: 

    from clef.code import *

After importing them you need to open a connection with the NCI MAS database to be able to run your queries::

    db = connect()
    s = Session()

The **search** function takes 3 inputs: the db session, the project (i.e. currently 'cmip5' or 'cmip6') and a dictionary containing the query constraints.::

    results = search(s, project='cmip5', **constraints)

The keys available to define your constraints depend on the project you are querying and the attributes stored by the database. You can use any of the *facets* used for ESGF but in future we will be adding other options based on extra fields which are stored as attributes.  

Examples
--------
::
    constraints = {'variable': 'tas', 'model': 'MIROC5', 'cmor_table': 'day', 'experiment': 'rcp85'}
    results = search(s, project='cmip5', **constraints)
    results[0]
    {'filenames': ['tas_day_MIROC5_rcp85_r1i1p1_20060101-20091231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20500101-20591231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20200101-20291231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20800101-20891231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20600101-20691231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20100101-20191231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20900101-20991231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20700101-20791231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20400101-20491231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_20300101-20391231.nc', 'tas_day_MIROC5_rcp85_r1i1p1_21000101-21001231.nc'], 'project': 'CMIP5', 'institute': 'MIROC', 'model': 'MIROC5', 'experiment': 'rcp85', 'frequency': 'day', 'realm': 'atmos', 'r': '1', 'i': '1', 'p': '1', 'ensemble': 'r1i1p1', 'cmor_table': 'day', 'version': '20120710', 'variable': 'tas', 'pdir': '/g/data1b/al33/replicas/CMIP5/output1/MIROC/MIROC5/rcp85/day/atmos/day/r1i1p1/v20120710/tas', 'periods': [('20060101', '20091231'), ('20500101', '20591231'), ('20200101', '20291231'), ('20800101', '20891231'), ('20600101', '20691231'), ('20100101', '20191231'), ('20900101', '20991231'), ('20700101', '20791231'), ('20400101', '20491231'), ('20300101', '20391231'), ('21000101', '21001231')], 'fdate': '20060101', 'tdate': '21001231', 'time_complete': True}

**search** returns a list of dictionary, one for each dataset.
You can see from the first result the dictionary content, the last key *time_complete* is the result of a check run on the time axis beuilt by joining together the files periods. If the time axis is contiguos is true, otherwise is False.
NB that this has been calculated only using the dates listed in the files, the actual timesteps have not been checked.

Both the keys and values of the constraints get checked before being passed to the query function. This means that if you passed a key or a value that does not exist for the chosen project, the function will print a list of valid values and then exit.
Let's re-write the constraints dictionary to show an example.::

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'e': 'rcp85', 'activity':'CMIP'}
    results = search(s, project='cmip5', **constraints)
    Warning activity is not a valid constraint name
    Valid constraints are:
    dict_values([['source_id', 'model', 'm'], ['realm'], ['time_frequency', 'frequency', 'f'], ['variable_id', 'variable', 'v'], ['experiment_id', 'experiment', 'e'], ['table_id', 'table', 'cmor_table', 't'], ['member_id', 'member', 'ensemble', 'en', 'mi'], ['institution_id', 'institution', 'institute'], ['experiment_family']])

You can see that the function told us 'activity' is not a valid constraints for CMIP5, in fact that can be used only with CMIP6
NB. that the search accepted all the other abbreviations, we allowed more than one term to be used for each key. The full list is available from the github repository:
https://github.com/coecms/clef/blob/master/clef/data/valid_keys.json

More complex queries
We are adding functions that can facilitate more complex queries, an example is the 'matching' function
It is easier to understand how matching work starting from an example.
A user might want to get all the model/ensemble combinations which have both tasmin and tasmax 
To do this use the standard query I would have to do pass these constraints to a query
::    constraints = {'variable': 'tasmin', 'cmor_table': 'day', 'experiment': 'rcp85'}
found all the model/ensemble which have tasmin / rcp85 / day
then repeat the same for 'tasmax' and finally check which model/ensemble combinations have both.
The 'matching' function simplify all of this.
First of all I can pass to it multiple values::
    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85']}

Then I need define the attribute for which I want all the values to be present::
    allvalues=['variable']
I need to define what are the attributes whose combination define a simulation, model and ensemble, i.e. each model/ensemble combination define a simulation, in some cases you might want to add to these also the version::
    fixed=['model','ensemble']
Finally we call matching::
    results, selection = matching(s, allvalues, fixed, **constraints)
The function returns two lists, the first 'results' contains a dictionary for each simulation that has either tasmin or tasmax for {rcp85, day}.
The second 'selection' has only the simulations that has both 'tasmin' and 'tasmax'. 
Other examples
Find simulations which have 'tasmin' and 'tasmax' and both 'rcp85' and 'rcp45' experiments::
    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85', 'rcp45']}
    allvalues=['variable', 'experiment']
    fixed=['model','ensemble']
    results, selection = matching(s, allvalues, fixed, **constraints)
Find simulations which have 'tasmin' and 'tasmax' for either 'rcp85' or 'rcp45' experiments::
    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85', 'rcp45']}
    allvalues=['variable']
    fixed=['model','ensemble', 'experiment']
    results, selection = matching(s, allvalues, fixed, **constraints)

By default we are searching for CMIP5 if we want to do the same for CMIP6 we need to change the project value and use the right facet names::
Find simulations which have 'tasmin' and 'tasmax' for 'piControl' experiment::
    constraints = {'variable_id': ['tasmin','tasmax'], 'table_id': ['day'], 'experiment_id': ['piControl']}
    allvalues=['variable_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
In particular for CMIP6, for which data is still getting published, you might want to execute the same search on the remote ESGF data catalogue rather than locally. In that case we change the 'local' argument from its default value True to False::
    constraints = {'variable_id': ['tasmin','tasmax'], 'table_id': ['day'], 'experiment_id': ['piControl']}
    allvalues=['variable_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', local=False, **constraints)

NB currently using the abbreviated version for the constraints won't work, you will have to use the attributes full names. 

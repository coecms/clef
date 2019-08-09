Complex queries
===============

We are working on new functions that can facilitate more complex queries, an example is the *matching* function
It is easier to understand how matching work starting from an example.
A user might want to get all the model/ensemble combinations which have both tasmin and tasmax 
To do this use the standard query I would have to do pass these constraints to a query::
    constraints = {'variable': 'tasmin', 'cmor_table': 'day', 'experiment': 'rcp85'}
find all the model/ensemble which have tasmin / rcp85 / day
then repeat the same for 'tasmax' and finally check which model/ensemble combinations have both.
The *matching* function simplify all of this.
First of all I can pass to it multiple values::
    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85']}

Then I need define the attribute for which I want all the values to be present::
    allvalues=['variable']
I need to define what are the attributes whose combination define a simulation, model and ensemble, i.e. each model/ensemble combination define a simulation, in some cases you might want to add to these also the version::
    fixed=['model','ensemble']
Finally we call *matching*::
    results, selection = matching(s, allvalues, fixed, **constraints)
The function returns two lists, the first *results* contains a dictionary for each simulation that has either tasmin or tasmax for {rcp85, day}.
The second *selection* has only the simulations that has both *tasmin* and *tasmax*. 

Other examples
--------------
Find simulations which have *tasmin* and *tasmax* for both *rcp85* and *rcp45* experiments::
    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85', 'rcp45']}
    allvalues=['variable', 'experiment']
    fixed=['model','ensemble']
    results, selection = matching(s, allvalues, fixed, **constraints)
Find simulations which have *tasmin* and *tasmax* for either *rcp85* or *rcp45* experiments::
    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85', 'rcp45']}
    allvalues=['variable']
    fixed=['model','ensemble', 'experiment']
    results, selection = matching(s, allvalues, fixed, **constraints)

By default we are searching for CMIP5 if we want to do the same for CMIP6 we need to change the project value and use the right facet names
Find simulations which have *tasmin* and *tasmax* for *piControl* experiment::
    constraints = {'variable_id': ['tasmin','tasmax'], 'table_id': ['day'], 'experiment_id': ['piControl']}
    allvalues=['variable_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
In particular for CMIP6, for which data is still getting published, you might want to execute the same search on the remote ESGF data catalogue rather than locally. In that case we change the *local* argument from its default value True to False::
    constraints = {'variable_id': ['tasmin','tasmax'], 'table_id': ['day'], 'experiment_id': ['piControl']}
    allvalues=['variable_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', local=False, **constraints)

NB currently using the abbreviated version for the constraints keys won't work, you will have to use the attributes full names. 

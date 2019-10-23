Complex queries
===============

We are working on new functions that can facilitate more complex queries, an example is the *matching* function
It is easier to understand how matching work starting from an example.
We might want to get all the model/ensemble combinations which have both tasmin and tasmax 
To do this using the standard query we would have to do pass these constraints to the *search()* function::

    constraints = {'variable': 'tasmin', 'cmor_table': 'day', 'experiment': 'rcp85'}

which would select all the model/ensemble which have tasmin / rcp85 / day.
Then we would repeat the same for 'tasmax' and finally check which model/ensemble combinations have both.
The *matching()* function simplify all of this.
First of all, we can pass to it multiple values::

    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['day'], 'experiment': ['rcp85']}

Then we need define the attribute for which we want all the values to be present::

    allvalues=['variable']

We need to define what are the attributes whose combination define a simulation, model and ensemble, i.e. each model/ensemble combination define a simulation, in some cases you might want to add to these also the version::

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

By default we are querying CMIP5 if we want to do the same for CMIP6 we need to change the project value and use the right facet names
Find simulations which have *tasmin* and *tasmax* for *piControl* experiment::

    constraints = {'variable_id': ['tasmin','tasmax'], 'table_id': ['day'], 'experiment_id': ['piControl']}
    allvalues=['variable_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)

In particular for CMIP6, for which data is still getting published, you might want to execute the same query on the remote ESGF data catalogue rather than locally. In that case we change the *local* argument from its default value True to False::

    constraints = {'variable_id': ['tasmin','tasmax'], 'table_id': ['day'], 'experiment_id': ['piControl']}
    allvalues=['variable_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', local=False, **constraints)

NB currently using the abbreviated version for the constraints keys won't work, you will have to use the attributes full names. 
As for *search()*, *matching()* also take an additional argument *latest* which is by default True.

You can now call this function also from the command line::

   clef --local cmip6 -v tasmin -v tasmax  -t Amon -e piControl -mi r1i1p1f1  --and variable_id --and experiment_id
   AWI-CM-1-1-MR r1i1p1f1 {'v20181218'}
   BCC-CSM2-MR r1i1p1f1 {'v20181016'}
   ...
   MIROC6 r1i1p1f1 {'v20181212'}
   MRI-ESM2-0 r1i1p1f1 {'v20190222'}
   SAM0-UNICON r1i1p1f1 {'v20190323'}

You use the *--and* option to pass the *fixed* arguments, it assumes that *model* and *ensemble* define a simulation.



AND Filter
~~~~~~~~~~

We started adding additional features to CleF which allows more complex
queries. We started from the following case. Let’s say that you want to
find all the CMIP6 models that have both daily precipitation (pr) and
soil moisture (mrso) for a particular experiment(historical). Up to now
you would had to select separately both variables and then work out
which models had both on your own.

We will show how this work starting by using the actual function
interactively. There is also a command line option but it returns only a
list of the models. First of all, since we are potentially passing more
than one value to the query we are using lists in our *constraints*
dictionary. Then we need to define the attributes for which we want all
values to be present, only *variable_id* in this case. Finally we tell
the function which attributes define a simulation, this would most often
be *model* and *member*.::

    constraints = {'variable_id': ['pr','mrso'], 'frequency': ['mon'], 'experiment_id': ['historical']}
    allvalues = ['variable_id']
    fixed = ['source_id', 'member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)

The function returns the selected models/members combinations that have
both variables and the corresponding subset of the original query
*results*. NB currently using the abbreviated version for the
constraints keys won’t work, you will have to use the attributes full
names. You can see by printing the length of both lists and one of the
first item of *selection* that the results have been grouped by
models/ensembles and then filtered.::

    print(len(results),len(selection))
    selection[0]


    46 23

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'comb': {('mrso',), ('pr',)},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114'},
     'version': {'v20181114', 'v20181126'}}


The full definition the **matching()** shows all the function arguments:
 * matching(session, cols, fixed, project=‘CMIP5’, local=True,
            latest=True, \**kwargs)

From this you can see that like **search()** by default *project* is
‘CMIP5’ and *latest* is True. We didn’t have to use yet the *local*
argument which is True by default, we will see examples later where is
set to False so we can do the same query remotely.

AND filter on more than one attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can pass more than value for more than one attribute, let’s add
*piControl* to the experiment list.::

    constraints = {'variable_id': ['pr','mrso'], 'frequency': ['mon'], 'experiment_id': ['historical', 'piControl']}
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]


    100 29

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'comb': {('mrso',), ('pr',)},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Amon/pr/gn/v20181016',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Lmon/mrso/gn/v20181012'},
     'version': {'v20181012', 'v20181016', 'v20181114', 'v20181126'}}


As you can see we get now many more results but only a few more
combinations after applying the filter. This is because we are still
defining a simulation by using model and member combinations we haven’t
included experiment and the results for the two experiments are grouped
together, to fix this we need to add *experiment_id* to the *fixed*
list.::

    fixed = ['source_id', 'member_id','experiment_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]


    98 49

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'experiment_id': 'historical',
     'comb': {('mrso',), ('pr',)},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114'},
     'version': {'v20181114', 'v20181126'}}


If we wanted to find all models/members combinations which have both
variables and both experiments, then we should have kept *fixed* as it
was and add *experiment_id* to the *allvalues* list instead.::

    allvalues = ['variable_id', 'experiment_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]


    80 20

    {'source_id': 'BCC-CSM2-MR',
     'member_id': 'r1i1p1f1',
     'comb': {('mrso', 'historical'),
      ('mrso', 'piControl'),
      ('pr', 'historical'),
      ('pr', 'piControl')},
     'table_id': {'Amon', 'Lmon'},
     'pdir': {'/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Amon/pr/gn/v20181126',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Lmon/mrso/gn/v20181114',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Amon/pr/gn/v20181016',
      '/g/data1b/oi10/replicas/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Lmon/mrso/gn/v20181012'},
     'version': {'v20181012', 'v20181016', 'v20181114', 'v20181126'}}


AND filter applied to remote ESGF query
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can of course do the same query for CMIP5, in that case you can omit
*project* when calling the function since its default value is ‘CMIP5’.
Another default option is *local=True*, this says the function to perfom
this query directly on the local database if you want you can perform the same query on
the ESGF database, so you can see what has been published.::

    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['Amon'], 'experiment': ['historical','rcp26', 'rcp85']}
    allvalues = ['variable', 'experiment']
    fixed=['model','ensemble']
    results, selection = matching(s, allvalues, fixed, local=False, **constraints)
    print(len(results),len(selection))
    selection[0]


    1488 46

    {'model': 'CNRM-CM5',
     'ensemble': 'r1i1p1',
     'comb': {('tasmax', 'historical'),
      ('tasmax', 'rcp26'),
      ('tasmax', 'rcp85'),
      ('tasmin', 'historical'),
      ('tasmin', 'rcp26'),
      ('tasmin', 'rcp85')},
     'cmor_table': {'Amon'},
     'dataset_id': {'cmip5.output1.CNRM-CERFACS.CNRM-CM5.historical.mon.atmos.Amon.r1i1p1.v20110901|esg1.umr-cnrm.fr',
      'cmip5.output1.CNRM-CERFACS.CNRM-CM5.rcp26.mon.atmos.Amon.r1i1p1.v20110629|esg1.umr-cnrm.fr',
      'cmip5.output1.CNRM-CERFACS.CNRM-CM5.rcp85.mon.atmos.Amon.r1i1p1.v20110930|esg1.umr-cnrm.fr'},
     'version': {'v20110629', 'v20110901', 'v20110930'}}


Please note how I used different attributes names because we are
querying CMIP5 now. *comb* highlights all the combinations that have to
be present for a model/ensemble to be returned while we are getting a
dataset_id rather than a directory path.


AND filter on the command line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command line version of **matching** can be called using the *–and*
flag followed by the attribute for which we want all values, the flag
can be used more than once. By default model/ensemble combinations
define a simulation, and only model, ensemble and version are returned
as final result.::

    !clef --local cmip5 -v tasmin -v tasmax -e rcp26 -e rcp85 -e historical -t Amon --and variable


    ACCESS1.0 r1i1p1 {None}
    ...
    NorESM1-M r2i1p1 {'20110901'}
    NorESM1-M r3i1p1 {'20110901'}
    inmcm4 r1i1p1 {'20130207'}


The same will work for *–remote* and *cmip6*::

    !clef --remote cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id


    BCC-CSM2-MR r1i1p1f1 {'v20181016', 'v20181012'}
    BCC-ESM1 r1i1p1f1 {'v20181211', 'v20181214'}
    ...
    NorCPM1 r1i1p1f1 {'v20190914'}
    SAM0-UNICON r1i1p1f1 {'v20190910'}

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
values to be present, only ``variable_id`` in this case. Finally we tell
the function which attributes define a simulation, this would most often
be ``model`` and ``member``.

.. code::

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
models/ensembles and then filtered.

.. code::

    print(len(results),len(selection))
    selection.iloc[0,:]


.. parsed-literal::

    174 87

.. parsed-literal::

    comb                                          {(pr,), (mrso,)}
    frequency                                                {mon}
    version                                            {v20191108}
    path         {/g/data/fs38/publications/CMIP6/CMIP/CSIRO-AR...
    table_id                                          {Amon, Lmon}
    index                                               (322, 608)
    Name: (ACCESS-CM2, r1i1p1f1), dtype: object



The full definition the **matching()** shows all the function arguments:
>matching(session, cols, fixed, project=‘CMIP5’, local=True,
latest=True, \**kwargs)

From this you can see that like **search()** by default ``project`` is
‘CMIP5’ and ``latest`` is True. We didn’t have to use yet the ``local``
argument which is True by default, we will see examples later where is
set to False so we can do the same query remotely.

AND filter on more than one attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can pass more than value for more than one attribute, let’s add
*piControl* to the experiment list.

.. code::

    constraints = {'variable_id': ['pr','mrso'], 'frequency': ['mon'], 'experiment_id': ['historical', 'piControl']}
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection.iloc[0,:]


.. parsed-literal::

    275 93

.. parsed-literal::

    comb                                          {(pr,), (mrso,)}
    frequency                                                {mon}
    version                                 {v20191112, v20191108}
    path         {/g/data/fs38/publications/CMIP6/CMIP/CSIRO-AR...
    table_id                                          {Amon, Lmon}
    index                                     (322, 624, 680, 766)
    Name: (ACCESS-CM2, r1i1p1f1), dtype: object



As you can see we get now many more results but only a few more
combinations after applying the filter. This is because we are still
defining a simulation by using model and member combinations we haven’t
included experiment and the results for the two experiments are grouped
together, to fix this we need to add ``experiment_id`` to the *fixed*
list.

.. code::

    fixed = ['source_id', 'member_id','experiment_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection.iloc[0,:]


.. parsed-literal::

    270 135

.. parsed-literal::

    comb                                          {(pr,), (mrso,)}
    frequency                                                {mon}
    version                                            {v20191108}
    path         {/g/data/fs38/publications/CMIP6/CMIP/CSIRO-AR...
    table_id                                          {Amon, Lmon}
    index                                               (322, 680)
    Name: (ACCESS-CM2, r1i1p1f1, historical), dtype: object


If we wanted to find all models/members combinations which have both
variables and both experiments, then we should have kept *fixed* as it
was and add ``experiment_id`` to the *allvalues* list instead.

.. code::

    allvalues = ['variable_id', 'experiment_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection.iloc[0,:]


.. parsed-literal::

    168 42

.. parsed-literal::

    comb         {(mrso, piControl), (mrso, historical), (pr, p...
    frequency                                                {mon}
    version                                 {v20191112, v20191108}
    path         {/g/data/fs38/publications/CMIP6/CMIP/CSIRO-AR...
    table_id                                          {Amon, Lmon}
    index                                     (322, 624, 680, 766)
    Name: (ACCESS-CM2, r1i1p1f1), dtype: object


AND filter applied to remote ESGF query
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can of course do the same query for CMIP5, in that case you can omit
``project`` when calling the function since its default value is
‘CMIP5’. Another default option is *local=True*, this says the function
to perfom this query directly on the local database if you want you can
perform the same query on the ESGF database, so you can see what has
been published.

.. code::

    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['Amon'], 'experiment': ['historical','rcp26', 'rcp85']}
    allvalues = ['variable', 'experiment']
    fixed=['model','ensemble']
    results, selection = matching(s, allvalues, fixed, local=False, **constraints)
    print(len(results),len(selection))
    selection.iloc[0,:]


.. parsed-literal::

    1494 47

.. parsed-literal::

    comb          {(tasmax, historical), (tasmax, rcp26), (tasma...
    dataset_id    {cmip5.output1.CNRM-CERFACS.CNRM-CM5.historica...
    version              {(v20110629,), (v20110901,), (v20110930,)}
    cmor_table                                               {Amon}
    index         (422, 423, 424, 425, 426, 427, 476, 477, 478, ...
    Name: (CNRM-CM5, r1i1p1), dtype: object


Please note how I used different attributes names because we are
querying CMIP5 now. ``comb`` highlights all the combinations that have
to be present for a model/ensemble to be returned while we are getting a
``dataset_id`` rather than a directory path.

AND filter on the command line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command line version of **matching** can be called using the
``--and`` flag followed by the attribute for which we want all values,
the flag can be used more than once. By default model/ensemble
combinations define a simulation, and only model, ensemble and version
are returned as final result.

.. code::

    !clef --local cmip5 -v tasmin -v tasmax -e rcp26 -e rcp85 -e historical -t Amon --and variable


.. parsed-literal::

    ACCESS1.0 / r1i1p1 versions: 20120727, 20120115
    ACCESS1.0 / r2i1p1 versions: 20130726
    ACCESS1.0 / r3i1p1 versions: 20140402
    ...
    MRI-CGCM3 / r2i1p1 versions: 20120701
    MRI-CGCM3 / r3i1p1 versions: 20120701
    MRI-CGCM3 / r4i1p2 versions: 20120701
    MRI-CGCM3 / r5i1p2 versions: 20120701
    MRI-ESM1 / r1i1p1 versions: 20140210, 20130307
    NorESM1-M / r1i1p1 versions: 20120412
    NorESM1-M / r2i1p1 versions: 20120412
    NorESM1-M / r3i1p1 versions: 20120412
    inmcm4 / r1i1p1 versions: 20130207


The same will work for ``--remote`` and *cmip6*

.. code::

    !clef --remote cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id


.. parsed-literal::

    ACCESS-CM2 / r1i1p1f1 versions: v20191112
    ACCESS-ESM1-5 / r1i1p1f1 versions: v20191214
    AWI-ESM-1-1-LR / r1i1p1f1 versions: v20200212
    ...
    NorESM2-MM / r1i1p1f1 versions: v20191108
    SAM0-UNICON / r1i1p1f1 versions: v20190910
    TaiESM1 / r1i1p1f1 versions: v20200302, v20200211

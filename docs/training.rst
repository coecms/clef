
Using CleF - Climate Finder to discover ESGF data at NCI
========================================================

This notebook shows examples of how to use the CleF (Climate Finder)
python module to search for ESGF data on the NCI server. Currently the
tool is set up for CMIP5 and CMIP6 data, but other ESGF dataset like
CORDEX will be available in the future.

CleF is currently installed in the CMS conda module analysis3. This is
managed by the CMS and is available simply by running > module use
/g/data3/hh5/public/modules > module load conda/analysis3

You could use the module interactively, for the moment we will use its
command line options. Let’s start!

Command syntax
--------------

.. code:: ipython3

    # run this if you haven't done so already in the terminal
    #module use /g/data3/hh5/public/modules
    #module load conda/analysis3

.. code:: ipython3

    !clef

By simpling running the command **clef** with no arguments, the tool
shows the help message and then exits, basically it is equivalent to >
clef –help

We can see currently there are 3 sub-commands, **ds** to query non-ESGF
collections and one for each cmip dataset: **cmip5** and **cmip6**.
There are also five different options that can be passed before the
sub-commands, one we have already seen is *–help*. The others are used
to modify how the tool will deal with the main query output. We will
have a look at them and at **ds** later. Let’s start from quering some
CMIP5 data, to see what we can pass to the **cmip5** sub-command we can
simply run it with its *–help* option.

CMIP5
-----

.. code:: ipython3

    !clef cmip5 --help

Passing arguments and options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *help* shows all the constraints we can pass to the tool, there are
also some additional options which can change the way we run our query.
For the moment we can ignore these and use their default values. Some of
the constraints can be passed using an abbreviation,like *-v* instead of
*–variable*. This is handy once you are more familiar with the tool. The
same option can have more than one name, for example *–ensemble* can
also be passed as *–member*, this is because the terminology has changed
between CMIP5 and CMIP6. You can pass how many constraints you want and
pass the same constraint more than once. Let’s see what happens though
if we do not pass any constraint.

.. code:: ipython3

    !clef cmip5

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table day --ensemble r2i1p1s

Oops that wasn’t reasonable! I mispelled the ensemble “r2i1p1s” does not
exists and the tool is telling me it cannot find any matches.

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table days --ensemble r2i1p1

Made another spelling mistake, in this case the tool knows that I passed
a wrong value and lists for me all the available options for the CMOR
table. Eventually we are aiming to validate all the arguments we can,
although for some it is no possible to pass all the possible values
(ensemble for example).

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table day --ensemble r2i1p1

The tool first search on the ESGF for all the files that match the
constraints we passed. It then looks for these file locally and if it
finds them it returns their path on raijin. For all the files it can’t
find locally, the tool check an NCI table listing the downloads they are
working on. Finally it lists missing datasets which are in the download
queue, followed by the datasets that are not available locally and no
one has yet requested.

The tool list the datasets paths and dataset_ids, if you want you can
get a more detailed list by file by passing the *–format file* option.

The query by default returns the latest available version. What if we
want to have a look at all the available versions?

.. code:: ipython3

    !clef cmip5 --variable tasmin --experiment historical --table Amon -m ACCESS1.0 --all-versions --format file

The option *–all-versions* is the reverse of *–latest*, which is also
the default, so we get a list of all available versions. Since all the
ACCESS1.0 data is available on NCI (which is the authoritative source
for the ACCESS models) the tool doesn’t find any missing datasets and
let us know about it.

CMIP6
-----

.. code:: ipython3

    !clef cmip6 --help

The **cmip6** sub-command works in the same way but some constraints are
different. As well as changes in terminology CMIP6 has more attributes
(*facets*) that can be used to select the data. Examples of these are
the **activity** which groups experiments, **resolution** which is an
approximation of the actual resolution and **grid**.

Controlling the ouput: clef options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    !clef --local cmip6 -e 1pctCO2 -t Amon -v tasmax -v tasmin -g gr

In this example we used the *–local* option for the main command
**clef** to get only the local matching data path as output. Note also
that: - we are using abbreviations for the options where available; - we
are passing the variable *-v* option twice; - we used the CMIP6 specific
option *-g/–grid* to search for all data that is not on the model native
grid. This doesn’t indicate a grid common to all the CMIP6 output only
to the model itself, the same is true for member_id and other
attributes.

*–local* is actually executing the query directly on the NCI MAS
database, which is different from the default query where the search is
executed first on the ESGF and then its results are matched locally. In
the example above the final result is exactly the same, whichever way we
perform the query. This way of searching can give you more results if a
node is offline or if a version have been unpublished from the ESGF but
is still available locally.

.. code:: ipython3

    !clef --missing cmip6 -e 1pctCO2 -v clw -v clwvi -t Amon -g gr

This time we used the *–missing* option and the tool returned only the
results matching the constraints that are available on the ESGF but not
locally (we changed variables to make sure to get some missing data
back).

.. code:: ipython3

    !clef --remote cmip6 -e 1pctCO2 -v tasmin -t Amon -g gr

The *–remote* option returns the Dataset_ids of the data matching the
constraints, regardless that they are available locally or not.

.. code:: ipython3

    !clef --remote cmip6 -e 1pctCO2 -v tasmin -t Amon -g gr -mi r1i1p1f2 --format file

Running the same command with the option *–format file* after the
sub-command, will return the File_ids instead of the default
Dataset_ids. Please note that *–local*, *–remote* and *–missing*
together with *–request*, which we will look at next, are all options of
the main command **clef** and they need to come before any sub-commands.

Requesting new data
-------------------

What should we do if we found out there is some data we are interested
to that has not been downloaded or requested yet? This is a complex data
collection, NCI, in consultation with the community, decided the best
way to manage it was to have one point of reference. Part of this
agreement is that NCI will download the files and update the database
that **clef** is interrrogating. After consultation with the community a
priority list was decided and NCI has started downloading anything that
falls into it as soon as become available. Users can then request from
the NCI helpdesk, other combinations of variables, experiments etc that
do not fall into this list. The list is available from the NCI climate
confluence website: Even without consulting the list you can use
**clef**, as we demonstrated above, to search for a particular dataset,
if it is not queued or downloaded already **clef** will give you an
option to request it from NCI. Let’s see how it works.

.. code:: bash

    %%bash
    clef --request cmip6 -e 1pctCO2 -v clw -v clwvi -t Amon -g gr
    no

We run the same query which gave us as a result 4 missing datasets but
this time we used the *–request* option after **clef**. The tool will
execute the query remotely, then look for matches locally and on the NCI
download list. Having found none gives as an option of putting in a
request. It will accept any of the following as a positive answer: > Y
YES y yes

With anything else or if you don’t pass anything it will assume you
don’t want to put in a request. It still saved the request in a file we
can use later.

.. code:: ipython3

    !cat CMIP6_*.txt

If I answered ‘yes’ the tool would have sent an e-mail to the NCI
helpdesk with the text file attached, NCI can pass that file as input to
their download tool and queue your request. NB if you are running clef
from raijin you cannot send an e-mail so in that case the tool will
remind you you you need to send an e-mail to the NCI helpdesk yourself
to finalise the request.

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

Both the keys and values of the constraints get checked before being
passed to the query function. This means that if you passed a key or a
value that doesn’t exist for the chosen project, the function will print
a list of valid values and then exit. Let’s re-write the constraints
dictionary to show an example.

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'activity': 'CMIP'}
    results = search(s, project='CMIP5', **constraints)

You can see that the function told us ‘activity’ is not a valid
constraints for CMIP5, in fact that can be used only with CMIP6 NB. that
the function accepted all the other abbreviations, there’s a few terms
that can be used for each key. The full list of valid keys is available
from from the github repository:
https://github.com/coecms/clef/blob/master/clef/data/valid_keys.json

.. code:: ipython3

    constraints = {'v': 'tas', 'm': 'MIROC5', 'table': 'day', 'experiment': 'rcp85', 'member': 'r1i1p1'}
    results = search(s, project='CMIP5', **constraints)

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

    constraints = {'v': ['tasmin','tasmax'], 'm': ['MIROC5','MIROC4h'],
                   'table': ['day'], 'experiment': ['rcp85'], 'member': ['r1i1p1']}
    results, paths = call_local_query(s, project='CMIP5', **constraints)

Because this function was created to deliver results for the command
line local query option, as well as the list of results, it also outputs
a list of their paths. Under the hood this function works out all the
combinations of the arguments you passed and will run **search()** for
each of them, before doing so will also run other functions that check
that the values and keys passed to the function are valid. The extra
argument *oformat* is necessary to resolve the command line *–format*
option. This can be ‘file’ or ‘dataset’, with the last being the
default. It influences the *paths* output but no *results* which will
contain all the datasets information including filenames.

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
be *model* and *member*.

.. code:: ipython3

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

.. code:: ipython3

    print(len(results),len(selection))
    selection[0]

The full definition the **matching()** shows all the function arguments:
>matching(session, cols, fixed, project=‘CMIP5’, local=True,
latest=True, \**kwargs)

From this you can see that like **search()** by default *project* is
‘CMIP5’ and *latest* is True. We didn’t have to use yet the *local*
argument which is True by default, we will see examples later where is
set to False so we can do the same query remotely.

AND filter on more than one attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can pass more than value for more than one attribute, let’s add
*piControl* to the experiment list.

.. code:: ipython3

    constraints = {'variable_id': ['pr','mrso'], 'frequency': ['mon'], 'experiment_id': ['historical', 'piControl']}
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]

As you can see we get now many more results but only a few more
combinations after applying the filter. This is because we are still
defining a simulation by using model and member combinations we haven’t
included experiment and the results for the two experiments are grouped
together, to fix this we need to add *experiment_id* to the *fixed*
list.

.. code:: ipython3

    fixed = ['source_id', 'member_id','experiment_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]

If we wanted to find all models/members combinations which have both
variables and both experiments, then we should have kept *fixed* as it
was and add *experiment_id* to the *allvalues* list instead.

.. code:: ipython3

    allvalues = ['variable_id', 'experiment_id']
    fixed=['source_id','member_id']
    results, selection = matching(s, allvalues, fixed, project='CMIP6', **constraints)
    print(len(results),len(selection))
    selection[0]

AND filter applied to remote ESGF query
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can of course do the same query for CMIP5, in that case you can omit
*project* when calling the function since its default value is ‘CMIP5’.
Another default option is *local=True*, this says the function to perfom
this query directly on MAS if you want you can perform the same query on
the ESGF database, so you can see what has been published.

.. code:: ipython3

    constraints = {'variable': ['tasmin','tasmax'], 'cmor_table': ['Amon'], 'experiment': ['historical','rcp26', 'rcp85']}
    allvalues = ['variable', 'experiment']
    fixed=['model','ensemble']
    results, selection = matching(s, allvalues, fixed, local=False, **constraints)
    print(len(results),len(selection))
    selection[0]

Please note how I used different attributes names because we are
querying CMIP5 now. *comb* highlights all the combinations that have to
be present for a model/ensemble to be returned while we are getting a
dataset_id rather than a directory path.

AND filter on the command line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The command line version of **matching()** can be called using the
*–and* flag followed by the attribute for which we want all values, the
flag can be used more than once. By default model/ensemble combinations
define a simulation, and only model, ensemble and version are returned
as final result.

.. code:: ipython3

    !clef --local cmip5 -v tasmin -v tasmax -e rcp26 -e rcp85 -e historical -t Amon --and variable

The same will work for *–remote* and *cmip6*

.. code:: ipython3

    !clef --remote cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id

New features
------------

We are in the process of adding some new output features following a
user request. These are currently only available in the development
version clef-test. To use this version: > module load conda > conda
activate clef-test

.. code:: ipython3

    !conda activate clef-test

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

    !clef --local cmip6 -v pr -v mrso -e piControl  -mi r1i1p1f1 --frequency mon --and variable_id --csv

.. code:: ipython3

    !head -n 4 CMIP6_query.csv

Query summary option
~~~~~~~~~~~~~~~~~~~~

The *–stats* option added to the command line will print a summary of
the query results Currently it prints the following: \* total number of
models, followed by their names \* total number of unique
model-ensembles/members combinations \* number of models that have N
ensembles/members, followed by their names

.. code:: ipython3

    !clef --local cmip5 -v pr -v mrso -e piControl --frequency mon --stats

Searching for other climate datasets: ds
----------------------------------------

Let’s get back to the command line now and have a look at the third
command **ds**\  This command let you query a separate database that
contains information on other climate datasets which are available on
raijin.

.. code:: ipython3

    !clef ds --help

| clef ds
| with no other argument will return a list of the local datasets
  available in the database. NB this is not an exhaustive list of the
  climate collections at NCI and not all the datasets already in the
  database have been completed.

.. code:: ipython3

    !clef ds

If you specify any of the variable options then the query will return a
list of variables rather then datasets. Since variables can be named
differently among datasets, using the *standard_name* or *cmor_name*
options to identify them is the best option.

.. code:: ipython3

    !clef ds -f netcdf --standard-name air_temperature

This returns all the variable available as netcdf files and with
air_temperature as standard_name. NB for each variable a path structure
is returned.

.. code:: ipython3

    !clef ds -f netcdf --cmor-name ta

This returns a subset of the previous query using the cmor_name to
clearly identify one kind of air_temperature.

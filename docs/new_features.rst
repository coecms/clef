New features
~~~~~~~~~~~~
This is an overview of some of functionalities we are working on or have recently released. Examples are included in the training section.

CSV file output
---------------
The *-–csv* option added to the command line will output the query
results in a csv file. Rather than getting only the files path, it will
list all the available attributes. This currently works with the
*–-local* iand *--remote* options, it does not yet work for the standard search.

The csv file name will be <project>_query.csv .

Query summary option
--------------------
The *-–stats* option added to the command line will print a summary of
the query results Currently it prints the following:
 * total number of models, followed by their names
 * total number of unique model-ensembles/members combinations
 * number of models that have N ensembles/members, followed by their names

*--stats* works when *--local* or *--remote* are specified but not with the default query

Errata and esdoc
----------------
There is some work in progress to add functionalities to interact with the ESDOC and the Errata ESGF systems. For the moment these are available only using clef interactively and not via the command line. 

Extra features
~~~~~~~~~~~~
This is an overview of some of the functionalities we added more recently. Examples are included in the training section.

CSV file output
---------------
The *-–csv* option added to the command line will output the query
results in a csv file. Rather than getting only the files path, it will
list all the available attributes. This currently works with the
*–-local* and *--remote* options, it does not yet work for the standard search.

The csv file name will be <project>_query.csv .

Query summary option
--------------------
The *-–stats* option added to the command line will print a summary of
the query results Currently it prints the following:
 * total number of models, followed by their names
 * total number of unique model-ensembles/members combinations
 * number of models that have N ensembles/members, followed by their names

*--stats* works when *--local* or *--remote* are specified but not with the default query

Citations list option
---------------------
The *--cite* option added to the command line will create a file containing the citations of all the datasets returned by the query. It retrieves the citation information from the DKRZ WDCC server (https://cera-www.dkrz.de/WDCC). This provides citation information only for CMIP6, so this flag is only available with the *cmip6* sub-command. Currently is only available when running clef with the *--local* or *--remote* flags.
The citation lists is saved in a file calledd *cmip_citations.txt* in the working directory.

Errata and esdoc
----------------
There is some work in progress to add functionalities to interact with the ESDOC and the Errata ESGF systems. For the moment these are available only using clef interactively and not via the command line. 

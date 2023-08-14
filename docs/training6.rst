More tips on queries
~~~~~~~~~~~~~~~~~~~~

About experiment_family
^^^^^^^^^^^^^^^^^^^^^^^

``experiment_family`` is a facet present only for CMIP5 and CORDEX. It
allows you to select all the experiments following in the same category.
The correspondent in CMIP6 is ``activity``. However, not all experiments
belong to a family and searching for both ``experiment`` and
``experiment_family`` at the same time can give unexpected results.
Let’s look at an example, if I want to get all the rcps experiments and
historical I might be tempted to pass them as constraints in the same
query:

.. code::

    !clef cmip5 -m CMCC-CM -e historical --experiment_family RCP -t Omon -v tos -en r1i1p1

.. parsed-literal::

    ERROR: No matches found on ESGF, check at https://esgf.nci.org.au/search/esgf-nci?query=&type=File&distrib=True&replica=False&latest=True&project=CMIP5&ensemble=r1i1p1&experiment=historical&model=CMCC-CM&cmor_table=Omon&variable=tos&experiment_family=RCP


The ESGF query uses an *AND* operator for all the constraints we pass.
We couldn’t find any matches because both the ``experiment`` and
``experiment_family`` constraints have to be satiflied. Similarly if we
pass rcp45 as experiment as well as the family RCP we will only get the
rcp45 results.

.. code::

    !clef cmip5 -m CMCC-CM -e rcp45 --experiment_family RCP -t Omon -v tos -en r1i1p1

.. parsed-literal::

    /g/data/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20120518/tos/
    /g/data/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20170725/tos/
    
    Everything available on ESGF is also available locally


Finally, it is now possible to use ``experiment_family`` also in the
local search:

.. code::

    !clef --local cmip5 -m CMCC-CM --experiment_family RCP -t Omon -v tos -en r1i1p1


.. parsed-literal::

    /g/data/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20120518/tos
    /g/data/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp45/mon/ocean/Omon/r1i1p1/v20170725/tos
    /g/data/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp85/mon/ocean/Omon/r1i1p1/v20120528/tos
    /g/data/al33/replicas/CMIP5/combined/CMCC/CMCC-CM/rcp85/mon/ocean/Omon/r1i1p1/v20170725/tos


Citation list option
~~~~~~~~~~~~~~~~~~~~

CleF has functions that retrieve errata associated to a file and the
documents available in the ESDOC system. Most of these functionalities
are currently working only when you use clef interactively. However,
since version 1.2 we added a flag to retrieve citations also using the
command line. The ``--cite`` option added to the command line will
create a file containing the citations of all the datasets returned by
the query. It retrieves the citation information from the DKRZ WDCC
server (https://cera-www.dkrz.de/WDCC). This provides citation
information only for CMIP6, so this flag is only available with the
**cmip6** sub-command. As for the other flags illustrated above, this
option works when you select either ``--local`` or ``--remote`` queries.

.. code::

    !clef --remote cmip6 -v clt  -e historical -t day  -mi r1i1p1f1 --cite


.. parsed-literal::

    CMIP6.CMIP.AS-RCEC.TaiESM1.historical.r1i1p1f1.day.clt.gn.v20200626
    CMIP6.CMIP.AWI.AWI-ESM-1-1-LR.historical.r1i1p1f1.day.clt.gn.v20200212
    ...
    CMIP6.CMIP.NUIST.NESM3.historical.r1i1p1f1.day.clt.gn.v20190812
    CMIP6.CMIP.SNU.SAM0-UNICON.historical.r1i1p1f1.day.clt.gn.v20190323
    Saving to cmip_citations.txt


The citations are listed in a cmip_citations.txt file in the current
directory.

.. code::

    ! head -n 4 cmip_citations.txt 

.. parsed-literal::

    Lee, Wei-Liang; Liang, Hsin-Chien (2020). AS-RCEC TaiESM1.0 model output prepared for CMIP6 CMIP historical. Version v20200626. Earth System Grid Federation. https://doi.org/10.22033/ESGF/CMIP6.9755
    Danek, Christopher; Shi, Xiaoxu; Stepanek, Christian; Yang, Hu; Barbi, Dirk; Hegewald, Jan; Lohmann, Gerrit (2020). AWI AWI-ESM1.1LR model output prepared for CMIP6 CMIP historical. Version v20200212. Earth System Grid Federation. https://doi.org/10.22033/ESGF/CMIP6.9328
    Wu, Tongwen; Chu, Min; Dong, Min; Fang, Yongjie; Jie, Weihua; Li, Jianglong; Li, Weiping; Liu, Qianxia; Shi, Xueli; Xin, Xiaoge; Yan, Jinghui; Zhang, Fang; Zhang, Jie; Zhang, Li; Zhang, Yanwu (2018). BCC BCC-CSM2MR model output prepared for CMIP6 CMIP historical. Version v20181127. Earth System Grid Federation. https://doi.org/10.22033/ESGF/CMIP6.2948
    Zhang, Jie; Wu, Tongwen; Shi, Xueli; Zhang, Fang; Li, Jianglong; Chu, Min; Liu, Qianxia; Yan, Jinghui; Ma, Qiang; Wei, Min (2018). BCC BCC-ESM1 model output prepared for CMIP6 CMIP historical. Version v20181220. Earth System Grid Federation. https://doi.org/10.22033/ESGF/CMIP6.2949


Please note that some of the more recently published datasets might not
have citations information available yet on the WDCC server. CleF
retrieves the information from different fields and them put them
together to form a correct citation in the required format. If some of
these fields are not available the citation might be incomplete, so
always check the entire file before using it. In particular the part of
the citation that includes the doi will be missing.


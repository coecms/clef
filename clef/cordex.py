#!/usr/bin/env python
#
# Copyright 2019 Scott Wales
#
# Author: Scott Wales <scott.wales@unimelb.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from clef.esgf import esgf_query
import functools
import click


def tidy_facet_count(v):
    return v[::2]


@functools.lru_cache()
def get_facets(project):
    q = esgf_query(limit=0, project=project, type="Dataset", facets="*")

    q = {k: tidy_facet_count(v) for k, v in q["facet_counts"]["facet_fields"].items()}

    return q


cli_facets = {
    "institute": {
        "help": "identifier for the institution that is responsible for the scientific aspects of the CORDEX simulation",
        "controlled_vocab": True,
    },
    "experiment": {
        "help": "CMIP5 experiment of driving GCM or 'evaluation' for re-analysis",
        "controlled_vocab": True,
    },
    "ensemble": {
        "help": "Ensemble member of the driving GCM",
        "controlled_vocab": True,
    },
    "domain": {"help": "CORDEX region name", "controlled_vocab": True},
    "variable": {"help": "Variable name in file", "controlled_vocab": True},
    "cf_standard_name": {"help": "CF-Conventions name of the variable"},
    "rcm_version": {
        "help": "Identifier for reruns with perturbed parameters or smaller RCM release upgrades",
        "controlled_vocab": True,
    },
    "rcm_name": {"help": "Identifier of the CORDEX RCM", "controlled_vocab": True},
    "driving_model": {
        "help": "Model/analysis used to drive the model (eg. ECMWF­ERAINT)",
        "controlled_vocab": True,
    },
    "time_frequency": {"help": "Output frequency indicator", "controlled_vocab": True},
    "version": {"help": "Data publication version", "controlled_vocab": True},
}


class CordexCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        facets = get_facets(project="CORDEX")
        for k, v in cli_facets.items():
            opt = click.Option(
                [f"--{k}"], help=v["help"], multiple=True, metavar="FACET"
            )

            if v.get("controlled_vocab", False):
                opt.type = click.Choice(facets[k], case_sensitive=False)

            self.params.append(opt)

        opt = click.Option(
            ["--and", "and_attr"],
            multiple=True,
            type=click.Choice(cli_facets.keys()),
            help="Attributes for which we want to add AND filter, i.e. -v tasmin -v tasmax --and variable_id will return only model/ensemble that have both",
        )
        self.params.append(opt)

#!/usr/bin/env python
# Copyright 2017 ARC Centre of Excellence for Climate Extremes 
# author: Scott Wales <scott.wales@unimelb.edu.au>
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

# From https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/PGValues


from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FromClause


class values(FromClause):
    named_with_column = True

    def __init__(self, columns, *args, **kw):
        self._column_args = columns
        self.list = args
        self.alias_name = self.name = kw.pop('alias_name', None)

        if len(args) == 0:
            raise Exception("No entries in VALUES table")

    def _populate_column_collection(self):
        for c in self._column_args:
            c._make_proxy(self)


@compiles(values)
def compile_values(element, compiler, asfrom=False, **kw):
    columns = element.columns
    v = "VALUES %s" % ", ".join(
        "(%s)" % ", ".join(
                compiler.render_literal_value(elem, column.type)
                for elem, column in zip(tup, columns))
        for tup in element.list
    )
    if asfrom:
        if element.alias_name:
            v = "(%s) AS %s (%s)" % (v, element.alias_name, (", ".join(c.name for c in element.columns)))
        else:
            v = "(%s)" % v
    return v

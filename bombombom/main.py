#!/usr/bin/env python

import typer
import json
import sys
import re
from enum import Enum
from typing import List, Annotated
from pathlib import Path

from .def_parser import parse_def_file
from .kicad_bom import KicadBOM
from .filter import filter_components, generate_fields_in_groups, filter_groups
from .grouping import group_components, flatten_groups
from .collapse import collapse_fields_in_flat_groups
from .tabulate import tabulate
from .partdb import PartDB

class Action(str, Enum):
    table = "table"
    json_flat = "json-flat"
    json_by_instance = "json-by-instance"
    json_collapsed = "json-collapsed"
    upload_bom_to_partdb = "upload-bom-to-partdb"

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(list(obj))
        return json.JSONEncoder.default(self, obj)

def cli(
    schematics: List[str],
    bomdef: Annotated[str, typer.Option(help='YAML file with the BOM definition')],
    project_name: Annotated[str, typer.Option(help='Name of partdb project (used when action is upload_bom_to_partdb)')] = '',
    do: Annotated[Action, typer.Option(help='What action to do')] = Action.table,
):
    bomdef = parse_def_file(bomdef)
    boms = [_bom_from_sch_arg(sch) for sch in schematics]
    components = sum([bom.components() for bom in boms], [])
    components = filter_components(components, bomdef['prefilter'])
    groups = group_components(components, bomdef['grouping'])
    if 'partdb' in bomdef and bomdef['partdb']['match_parts']:
        pdb = PartDB(bomdef['partdb'])
        groups = pdb.add_partdb_fields_to_groups(groups)
    generate_fields_in_groups(groups, bomdef['generate_fields'])
    groups = filter_groups(groups, bomdef['filter'])
    if do.value == Action.json_by_instance:
        _dump_json(groups)
        return
    flat_groups = flatten_groups(groups)
    if do.value == Action.upload_bom_to_partdb:
        pdb.upload_bom_to_partdb(project_name, groups, flat_groups)
        return
    if do.value == Action.json_flat:
        _dump_json(flat_groups)
        return
    field_data = collapse_fields_in_flat_groups(flat_groups, bomdef['collapse'])
    if do.value == Action.json_collapsed:
        _dump_json(field_data)
        return
    if do.value == Action.table:
        tabulate(field_data, bomdef['tabulate'], sys.stdout)
        return

def _bom_from_sch_arg(sch):
    try:
        _, count, sch = re.split(r'^([0-9]+)\*', sch)
    except ValueError:
        count = 1
    return KicadBOM.read_from_sch_file(sch, board_count=int(count))

def _dump_json(data):
    json.dump(data, sys.stdout, indent=4, cls=SetEncoder)

def main():
    typer.run(cli)

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import typer
import json
from typing import List, Annotated
from pathlib import Path

from .def_parser import parse_def_file
from .kicad_bom import KicadBOM
from .filter import filter_components, generate_fields_in_groups, filter_groups
from .grouping import group_components, flatten_groups

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def cli(
    bomdef: Annotated[str, typer.Option(help='YAML file with the BOM definition')],
    filenames: List[Path]
):
    bomdef = parse_def_file(bomdef)
    boms = [KicadBOM.read_from_sch_file(sch) for sch in filenames]
    components = sum([bom.components() for bom in boms], [])
    components = filter_components(components, bomdef['prefilter'])
    groups = group_components(components, bomdef['grouping'])
    generate_fields_in_groups(groups, bomdef['generate_fields'])
    groups = filter_groups(groups, bomdef['filter'])
    groups = flatten_groups(groups)

    print(json.dumps(groups, indent=4, cls=SetEncoder))

def main():
    typer.run(cli)

if __name__ == '__main__':
    main()

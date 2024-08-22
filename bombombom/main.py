#!/usr/bin/env python

import typer
import json
from typing import List, Annotated
from pathlib import Path

from .def_parser import parse_def_file
from .kicad_bom import KicadBOM
from .filter import filter_components

def cli(
    bomdef: Annotated[str, typer.Option(help='YAML file with the BOM definition')],
    filenames: List[Path]
):
    bomdef = parse_def_file(bomdef)
    boms = [KicadBOM.read_from_sch_file(sch) for sch in filenames]
    components = sum([bom.components() for bom in boms], [])
    components = filter_components(components, bomdef['prefilter'])

    print(json.dumps(components, indent=4))

def main():
    typer.run(cli)

if __name__ == '__main__':
    main()

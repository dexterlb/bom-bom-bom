#!/usr/bin/env python

import typer
from typing import List
from pathlib import Path
from .kicad_bom import KicadBOM
import json

def cli(filenames: List[Path]):
    boms = [KicadBOM.read_from_sch_file(sch) for sch in filenames]
    components = sum([bom.components() for bom in boms], [])
    print(json.dumps(components, indent=4))

def main():
    typer.run(cli)

if __name__ == '__main__':
    main()

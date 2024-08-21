#!/usr/bin/env python

import typer
from typing import List
from pathlib import Path
from .kicad_bom import KicadBOM

def cli(filenames: List[Path]):
    boms = [KicadBOM.read_from_sch_file(sch) for sch in filenames]
    print(boms[0].netlist_sexpr)

def main():
    typer.run(cli)

if __name__ == '__main__':
    main()

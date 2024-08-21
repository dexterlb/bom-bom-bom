#!/usr/bin/env python

import typer
from typing import List
from pathlib import Path
from .kicad_bom import KicadBOM

def main(filenames: List[Path]):
    boms = [KicadBOM.read_from_sch_file(sch) for sch in filenames]
    print(boms[0].netlist_text)

typer.run(main)

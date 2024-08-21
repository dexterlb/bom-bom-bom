import tempfile
import subprocess
import sexpdata

class KicadBOM:
    @classmethod
    def read_from_sch_file(klass, path: str):
        with tempfile.NamedTemporaryFile(delete_on_close=False, mode='w+t') as netlist_f:
            convert_cmd = [
                'kicad-cli', 'sch', 'export', 'netlist',
                '-o', netlist_f.name,
                path,
            ]
            subprocess.run(convert_cmd, capture_output=True, check=True)
            return klass.read_from_netlist(netlist_f)

    @classmethod
    def read_from_netlist_file(klass, path: str):
        with open(path, 'r') as f:
            return klass.read_from_netlist(f)

    @classmethod
    def read_from_netlist(klass, f):
        return klass(sexpdata.load(f))

    def __init__(self, netlist_sexpr):
        self.netlist_sexpr = netlist_sexpr

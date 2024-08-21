import tempfile
import subprocess
import sexpdata
import os.path

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
        if netlist_sexpr[0].value() != 'export':
            raise RuntimeError('this does not look like a KiCAD netlist')
        self.netlist_sexpr = netlist_sexpr

    def dump_netlist(self):
        return sexpdata.dumps(self.netlist_sexpr, pretty_print=True)

    def components(self):
        src_name = self.src_name()
        component_sexprs = _find_key(self.netlist_sexpr, 'components')
        return [_make_component_data(cs, src_name) for cs in component_sexprs]

    def src_name(self):
        design = _find_key(self.netlist_sexpr, 'design')
        src = _find_key(design, 'source')
        src_filename = src[0]
        basename = os.path.basename(src_filename)
        return basename.removesuffix('.kicad_sch')

def _make_component_data(sexp, src_name):
    c = dict()
    c['src_name'] = src_name
    if sexp[0].value() != 'comp':
        raise RuntimeError(f'this does not look like a component entry (key was {str(sexp[0])})')
    c['ref'] = _find_key(sexp, 'ref')[0]
    c['value'] = _find_key(sexp, 'value')[0]
    fieldmap = _find_key(sexp, 'fields')
    c |= dict([_parse_field(f) for f in fieldmap])

    return c

def _parse_field(sexp):
    if sexp[0].value() != 'field':
        raise RuntimeError(f'this does not look like a field entry (key was {str(sexp[0])})')
    if sexp[1][0].value() != 'name':
        raise RuntimeError('second item in field entry is not called `name`')
    name = sexp[1][1].lower()
    try:
        value = sexp[2]
    except IndexError:
        value = None
    return name, value

def _find_key(sexp, k):
    if type(sexp) is not list:
        return None
    for item in sexp:
        if type(item) is not list:
            continue
        if len(item) == 0:
            continue
        if type(item[0]) is not sexpdata.Symbol:
            continue
        if item[0].value() == k:
            return item[1:]
    return None

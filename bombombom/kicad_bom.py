import tempfile
import subprocess
import sexpdata
import os.path

class KicadBOM:
    @classmethod
    def read_from_sch_file(klass, path: str, board_count=1):
        with tempfile.NamedTemporaryFile(delete_on_close=False, mode='w+t') as netlist_f:
            convert_cmd = [
                'kicad-cli', 'sch', 'export', 'netlist',
                '-o', netlist_f.name,
                path,
            ]
            subprocess.run(convert_cmd, capture_output=True, check=True)
            return klass.read_from_netlist(netlist_f, board_count)

    @classmethod
    def read_from_netlist_file(klass, path: str, board_count=1):
        with open(path, 'r') as f:
            return klass.read_from_netlist(f, board_count)

    @classmethod
    def read_from_netlist(klass, f, board_count=1):
        return klass(sexpdata.load(f), board_count)

    def __init__(self, netlist_sexpr, board_count=1):
        if netlist_sexpr[0].value() != 'export':
            raise RuntimeError('this does not look like a KiCAD netlist')
        self.netlist_sexpr = netlist_sexpr
        self._board_count = board_count
        self._board_name = self._determine_board_name()

    def dump_netlist(self):
        return sexpdata.dumps(self.netlist_sexpr, pretty_print=True)

    def components(self):
        component_sexprs = _find_key(self.netlist_sexpr, 'components')
        return [self._make_component_data(cs) for cs in component_sexprs]

    def _determine_board_name(self):
        design = _find_key(self.netlist_sexpr, 'design')
        src = _find_key(design, 'source')
        src_filename = src[0]
        basename = os.path.basename(src_filename)
        return basename.removesuffix('.kicad_sch')

    def _make_component_data(self, sexp):
        c = dict()
        c['_board_name'] = self._board_name
        c['_board_count'] = self._board_count
        if sexp[0].value() != 'comp':
            raise RuntimeError(f'this does not look like a component entry (key was {str(sexp[0])})')
        c['ref'] = _find_key(sexp, 'ref')[0]
        c['value'] = _find_key(sexp, 'value')[0]

        fieldmap = _find_key(sexp, 'fields')
        c |= dict([_parse_field(f) for f in fieldmap])

        props = _find_keys(sexp, 'property')
        c |= dict([_parse_prop(p) for p in props])

        return c

def _parse_field(sexp):
    if sexp[0].value() != 'field':
        raise RuntimeError(f'this does not look like a field entry (key was {str(sexp[0])})')
    return _parse_nameval(sexp[1:])

def _parse_prop(sexp):
    name, v = _parse_nameval(sexp)
    if type(v) is list:
        if v[0].value() != 'value':
            raise RuntimeError(f'this does not look like a property entry (key was {str(v[0])})')
        return name, v[1]
    else:
        return name, v

def _parse_nameval(sexp):
    if sexp[0][0].value() != 'name':
        raise RuntimeError('second item in field entry is not called `name`')
    name = sexp[0][1].lower()
    try:
        value = sexp[1]
    except IndexError:
        value = None
    return name, value

def _find_key(sexp, k):
    try:
        return next(_find_keys(sexp, k))
    except StopIteration:
        return None

def _find_keys(sexp, k):
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
            yield item[1:]

import strictyaml

def parse_def_file(filename):
    with open(filename, 'r') as f:
        return parse_def(f)

def parse_def(f):
    return strictyaml.load(f.read()).data

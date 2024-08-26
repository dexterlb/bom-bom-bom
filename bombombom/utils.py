import re
from numbers import Number

def sorted_h(items, sort_type, key=lambda x: x):
    if sort_type == 'lex':
        return sorted(items, key=lambda x: str(key(x)))
    elif sort_type == 'numeric':
        return sorted(items, key=lambda x: _numeric_key(x))

def _numeric_key(x):
    if isinstance(x, Number):
        return f'{x:08}'
    else:
        return ''.join((
            f'{int(item):08}' if re.match(r'^[0-9]+$', item) else item
            for item in re.split(r'([0-9]+)', str(x))
        ))

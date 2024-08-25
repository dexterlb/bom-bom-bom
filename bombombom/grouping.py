from collections import defaultdict
import re

def flattened_group_components(components, group_settings):
    return flatten_groups(group_components(components, group_settings))

def flatten_groups(groups):
    all_fields = set().union(*(set().union(*(set(c.keys()) for c in g)) for g in groups.values()))
    result = dict()
    for k, g in groups.items():
        result[k] = {f: _uniq([c[f] for c in g if f in c]) for f in all_fields}
    return result

def group_components(components, group_settings):
    d = defaultdict(list)
    for c in components:
        for item in _group_items(c, group_settings):
            d[item['_key']] += [item]
    return dict(d)

def _group_items(comp, group_settings):
    field_text = comp[group_settings['key_field']]
    splitter = group_settings.get('split_by')
    if splitter:
        keys = field_text.split(splitter)
    else:
        keys = [field_text]

    keys = [k.strip() for k in keys]

    for k in keys:
        if group_settings.get('parse_instances'):
            cnt, k = _multiplify(k)
        else:
            cnt = 1

        yield comp | {
            '_key': k,
            '_instance_count': cnt,
        }

def _multiplify(k):
    m = re.search(r'^([0-9]+)[\*x]\s*(.*)$', k)
    if not m:
        return 1, k
    return int(m.group(1)), m.group(2)

def _uniq(items):
    try:
        return set(items)
    except TypeError:
        return [items[0]] # we probably need to assert here that all items are the same somehow

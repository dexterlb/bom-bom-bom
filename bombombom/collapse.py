import re
from collections import defaultdict

def collapse_fields_in_flat_groups(fl, collapse_settings):
    return {k: collapse_fields(v, collapse_settings) for k, v in fl.items()}

def collapse_fields(dic, collapse_settings):
    dic = {**dic}
    for field in dic:
        if type(dic[field]) not in {list, set}:
            continue

        for collapser in collapse_settings:
            if re.match(collapser['match'], field):
                dic[field] = _collapse_field(dic[field], collapser)
                break
    return dic

def _collapse_field(items, collapser):
    if collapser['type'] == 'join':
        return collapser['by'].join((str(item) for item in _sorted_h(items)))
    elif collapser['type'] == 'group_by_prefix':
        prefix_lists = defaultdict(list)
        for item in items:
            k, v = item.split(collapser['split_prefix_by'], 1)
            prefix_lists[k] += [v]
        prefix_strings = {k: collapser['join_values_by'].join(vs) for k, vs in prefix_lists.items()}
        return collapser['join_groups_by'].join((
            k + collapser.get('join_prefix_by', collapser['split_prefix_by']) + prefix_strings[k]
            for k in sorted(prefix_lists.keys())
        ))
    else:
        raise RuntimeError(f'unknown collapser type: {collapser['type']}')

def _sorted_h(items):
    try:
        return sorted(items)
    except TypeError:
        return sorted(items, key=str)

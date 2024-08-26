import jinja2
from collections import defaultdict

def generate_fields_in_groups(groups, gen_settings):
    _generate_qty_fields_in_groups(groups)
    _generate_user_fields_in_groups(groups, gen_settings)

def _generate_user_fields_in_groups(groups, gen_settings):
    generators = [
        (f, jinja2.Template(template_str))
        for f, template_str in gen_settings.items()
    ]

    for group in groups.values():
        for comp in group:
            for f, gen in generators:
                comp[f] = gen.render(comp)

def _generate_qty_fields_in_groups(groups):
    for name, group in groups.items():
        qtys_by_board = defaultdict(int)
        qty = 0
        for comp in group:
            qty += comp['_instance_count'] * comp['_board_count']
            qtys_by_board[comp['_board_name']] += comp['_instance_count']
        for comp in group:
            comp['_qty'] = qty
            comp['_qtys_by_board'] = dict(qtys_by_board)


def filter_groups(groups, filter_specs):
    filters = [_build_filter(fs) for fs in filter_specs]
    res = {k: _run_filters_on_components(g, filters) for k, g in groups.items()}
    return {k: g for k, g in res.items() if g}

def filter_components(components, filter_specs):
    filters = [_build_filter(fs) for fs in filter_specs]
    return _run_filters_on_components(components, filters)

def _run_filters_on_components(components, filters):
    return [c for c in components if all((flt(c) for flt in filters))]

def _build_filter(filter_spec):
    if type(filter_spec) is str:
        templ = jinja2.Template('{{ ' + filter_spec + ' }}')

        def check(c):
            result = templ.render(c)
            if result == 'True':
                return True
            elif result == 'False':
                return False
            raise RuntimeError(f"The filter '{filter_spec}' returned '{str(result)}' instead of True or False")

        return check
    else:
        raise RuntimeError(f"I don't know how to build a filter from {str(filter_spec)}: {str(type(filter_spec))}")

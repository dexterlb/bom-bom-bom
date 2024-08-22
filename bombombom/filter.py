import jinja2

def generate_fields_in_groups(groups, gen_settings):
    generators = [
        (f, jinja2.Template(template_str))
        for f, template_str in gen_settings.items()
    ]

    for group in groups.values():
        for comp in group:
            for f, gen in generators:
                comp[f] = gen.render(comp)

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

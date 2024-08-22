import jinja2

def filter_components(components, filter_specs):
    filters = [_build_filter(fs) for fs in filter_specs]
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

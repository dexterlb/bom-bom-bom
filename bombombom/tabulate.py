import csv

def tabulate(field_data, settings, out):
    wr = csv.DictWriter(
        out,
        fieldnames=list(settings['columns'].keys()),
        dialect=settings['dialect'],
        extrasaction='ignore'
    )
    if settings['header']:
        wr.writerow(settings['columns'])
    for row in sorted(field_data.values(), key=lambda f: f[settings['sort_by']]):
        wr.writerow(row)

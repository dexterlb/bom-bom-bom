## bom bom bom

An opinionated command-line tool for managing [KiCAD](https://www.kicad.org/) BOM's
that works-for-me™.

Its key feature is that it supports multiple instances of boards and parts,
and can be used to generate cross-referenced BOMs for multiple boards at a time.

Run it like this:

```bash
$ bom-bom-bom --bomdef bom.yaml power_board.sch '2*'audio_board.sch
```

BOM generation is controlled by a YAML file that may look like this:

```yaml
prefilter:
  - 'exclude_from_bom is not defined'
  - 'dnp is not defined'

generate_fields:
  ref_with_instances: '{{ ref + ("*{}".format(_instance_count) if _instance_count > 1 else "") }}'
  ref_with_board: '{{ _board_name }}({{ "{}*".format(_board_count) if _board_count > 1 else "" }}{{ _qtys_by_board[_board_name] }})/{{ ref_with_instances }}'

filter:

grouping:
  key_field: 'part'
  split_by: ','
  parse_instances: true

collapse:
  - match: 'ref_with_board'
    type: 'group_by_prefix'
    split_prefix_by: '/'
    join_values_by: ' '
    join_groups_by: "\n"
    join_prefix_by: ': '
    sort_type: 'numeric'

  - match: '.*'
    type: 'join'
    by: "\n"
    sort_type: 'lex'

tabulate:
  sort_by: 'ref'
  sort_type: 'lex'
  header: true
  dialect: 'excel-tab'
  columns:
    _key: 'Part'
    _qty: 'Qty'
    ref_with_board: 'Refs'
    value: 'Value'
    footprint: 'Footprint'
```

This example yaml file assumes a field called `part` that uniquely identifies
each part that is sold separately. The tool will parse part field entries
that contain commas (`split_by`) or multipliers (`parse_instances`) as
multiple parts per symbol (e.g. a RPi Pico that is plugged into two headers
may be composed of three parts, like this: `RPi_Pico, 2*Header_1x20`.

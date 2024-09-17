import requests
import sys
import json
from .utils import sorted_h

class PartDB:
    def __init__(self, settings):
        self._settings = settings
        self.http = requests.Session()

    def add_partdb_fields_to_groups(self, groups):
        return {
            k: [f | {
                '_partdb': self.get_part_fields(k),
            } for f in v] for k, v in groups.items()
        }

    def upload_bom_to_partdb(self, project_name, unflat_groups, flat_groups):
        prj = self._get_project_by_name(project_name)
        if not prj:
            raise RuntimeError(f'no project with name {project_name} found')

        for old_bom_entry in list(self._get_bom_entries_by_project_id(prj['id'])):
            self._delete_item(old_bom_entry)

        for flat_group in flat_groups.values():
            entry = self._build_bom_entry(flat_group, unflat_groups, prj)
            self._req('api/project_bom_entries', method='POST', data=entry)

    def get_part_fields(self, key):
        fieldname = self._settings['search_field']
        fields = self._request_single_item('api/parts', fieldname, key)
        if fields:
            self._enrich_fields(fields)
        return fields

    def _get_field_from(self, field_setting_name, flat_group):
        field_name = self._settings.get(field_setting_name)
        if not field_name:
            return None
        if len(flat_group[field_name]) > 0:
            return list(flat_group[field_name])[0]

    def _build_bom_entry(self, flat_group, unflat_groups, prj):
        part = None
        name = list(flat_group['_key'])[0]
        if len(flat_group['_partdb']) > 0:
            part = list(flat_group['_partdb'])[0]
        footprint = self._get_field_from('field_footprint', flat_group)
        comment = self._get_field_from('field_comment', flat_group)

        mount_names = []
        for item in unflat_groups[name]:
            mn = item[self._settings['field_mount_names']]
            if item['_instance_count'] > 1:
                mount_names += [f'{mn}_{i + 1}' for i in range(item['_instance_count'])]
            else:
                mount_names += [mn]

        if footprint and part and part.get('footprint'):
            if footprint != part['footprint']['name']:
                raise RuntimeError(f'footprint {footprint} does not match partdb footprint for this part: {part['footprint']['name']}')

        return {
            'quantity': max(flat_group[self._settings['field_qty']]),
            'mountnames': ','.join(sorted_h(
                mount_names,
                self._settings['mount_names_sort_type'],
            )),
            'comment': comment,
            'project': prj,
            'part': part,
            'name': name,
            'price': None,
        }

    def _get_bom_entries_by_project_id(self, proj_id):
        return self._paginate(f'api/projects/{proj_id}/bom')

    def _enrich_fields(self, fields):
        fields['link'] = _url_join(self._settings['url'], f'en/part/{fields['id']}')
        fields['orderdetails_by_supplier'] = {}
        for ord in fields['orderdetails']:
            ord |= self._req(ord['@id'])
            fields['orderdetails_by_supplier'][ord['supplier']['full_path']] = ord

    def _get_project_by_name(self, project_name):
        return self._request_single_item('api/projects', 'name', project_name)

    def _delete_item(self, item):
        self._req(item['@id'], method='DELETE')

    def _paginate(self, path, method='GET', data=None, params={}):
        page = 1
        num_items = 0
        total_items = None

        while total_items is None or num_items < total_items:
            result = self._req(
                path=path, method=method, data=data,
                params={ 'itemsPerPage': 10 } | params | { 'page': page },
            )
            total_items = result['hydra:totalItems']
            num_items += len(result['hydra:member'])
            yield from result['hydra:member']
            page += 1

    def _request_single_item(self, url, k, v):
        results = self._req(url, params={k: v})['hydra:member']
        results = [r for r in results if r[k] == v]
        if len(results) > 1:
            raise RuntimeError(f'found more than one PartDB entries at {url} with filter {k}={v}')
        if len(results) == 0:
            return None
        return results[0]


    def _req(self, path, method='GET', data=None, params=None):
        headers = {
            'content-type': 'application/json',
            'Authorization': f'Bearer {self._settings['token']}'
        }
        url = _url_join(self._settings['url'], path)

        if params is None:
            params = {}

        resp = self.http.request(
            method, url,
            json=data,
            params=params, headers=headers,
        )
        resp.raise_for_status()

        if resp.text == '':
            return None

        try:
            return resp.json()
        except:
            raise RuntimeError(f'non-json response from api: {resp.text}')

def _url_join(*args):
    return "/".join(arg.strip("/") for arg in args)

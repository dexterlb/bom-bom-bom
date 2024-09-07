import requests
import sys
import json

class PartDB:
    def __init__(self, settings):
        self._settings = settings
        self.http = requests.Session()

    def add_partdb_fields_to_groups(self, groups):
        return {k: [f | { '_partdb': self.get_part_fields(k) } for f in v] for k, v in groups.items()}

    def upload_bom_to_partdb(self, project_name, field_data):
        prj = self._get_project_by_name(project_name)
        if not prj:
            raise RuntimeError(f'no project with name {project_name} found')
        for old_bom_entry in self._get_bom_entries_by_project_id(prj['id']):
            print(json.dumps(old_bom_entry, indent=4))
            self._delete_item(old_bom_entry)

        sys.exit(0)

    def get_part_fields(self, key):
        fieldname = self._settings['search_field']
        fields = self._request_single_item('api/parts', fieldname, key)
        if fields:
            self._enrich_fields(fields)
        return fields

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

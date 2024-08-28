import requests
import sys

class PartDB:
    def __init__(self, settings):
        self._settings = settings
        self.http = requests.Session()

    def add_partdb_fields_to_groups(self, groups):
        return {k: [f | { '_partdb': self.get_part_fields(k) } for f in v] for k, v in groups.items()}

    def get_part_fields(self, key):
        fieldname = self._settings['search_field']
        results = self._req(f'api/parts', params={fieldname: key})['hydra:member']
        results = [r for r in results if r[fieldname] == key]
        if len(results) > 1:
            raise RuntimeError(f'found more than one PartDB entries for part {key}')
        if len(results) == 0:
            return None

        fields = results[0]
        self._enrich_fields(fields)
        return fields

    def _enrich_fields(self, fields):
        fields['link'] = _url_join(self._settings['url'], f'en/part/{fields['id']}')
        fields['orderdetails_by_supplier'] = {}
        for ord in fields['orderdetails']:
            ord |= self._req(ord['@id'])
            fields['orderdetails_by_supplier'][ord['supplier']['full_path']] = ord

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

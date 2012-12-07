import os
import time
import datetime
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials

try:
    import json
except ImportError:
    import simplejson as json


class RequestFailed(BaseException): pass


class TracksAPI(object):
    token_uri = 'https://accounts.google.com/o/oauth2/token'
    scope_uri = 'https://www.googleapis.com/auth/tracks'
    base_url = None
    client_email = None

    def __init__(self, client_email, certificate, base_url="https://www.googleapis.com/tracks/v1/"):
        """Parameters:
        - client_email: is supplied by Google API Console
        - certificate: can be the P12 key itself or a file path which contains it."""

        self.base_url = base_url
        self.client_email = client_email

        if isinstance(certificate, basestring):
            if os.path.exists(certificate):
                self.certificate_key = self.load_key(certificate)
            else:
                self.certificate_key = certificate
        else:
            raise TypeError('certificate must be a P12 key string or a file path string.')

    def load_key(self, certificate_file):
        fp = file(certificate_file, 'rb')
        key = f.read()
        fp.close()
        return key

    def make_headers(self, body):
        return {
            'content-type': 'application/json',
            'content-length': str(len(body)),
        }

    def get_credentials(self):
        return SignedJwtAssertionCredentials(self.client_email, self.certificate_key, scope=self.scope_uri,
                token_uri=self.token_uri)

    def get_http_client(self):
        if not hasattr(self, '_http_client'):
            self._http_client = httplib2.Http()
            self._http_client = self.get_credentials().authorize(http)

        return self._http_client

    def request(self, method, data=None):
        http = self.get_http_client()
        url = self.base_url + method
        body = json.dumps(data) if data else ''

        headers, content = http.request(url, 'POST', headers=self.make_headers(body), body=body)

        if headers['status'] == '200' and headers['content-type'].startswith('application/json'):
            return json.loads(content)
        else:
            raise RequestFailed('Method "%s" returned: %s (%s)' % (method,content,headers['status']))

    # Methods for Entities

    def create_entity(self, name, type=None):
        """Paramters:
        - name: a simple string
        - type: can be AUTOMOBILE, TRUCK, WATERCRAFT or PERSON"""
        entity = {'name':name}
        if type:
            entity['type'] = type
        return self.create_entities([entity])

    def create_entities(self, entities):
        """Parameters:
        - entities: must be a list of dictionaries with keys "name" and "type" (optional)"""
        return self.request('entities/create', entities)

    def list_entities(self, entityIds=None, minId=None):
        """Parameters:
        - entityIds: a list with strings (no more than 256)
        - minId: for a contigous entities list starting from this ID"""
        params = {}

        if entityIds:
            params['entityIds'] = entityIds

        if minId:
            params['minId'] = minId

        return self.request('entities/list', params)

    def delete_entities(self, entityIds):
        """Parameters:
        - entityIds: a list with strings"""
        return self.request('entities/delete', {'entityIds':entityIds})

    # Methods for Collections

    def create_collection(self, name):
        """Parameters:
        - name: the new collection name"""
        return self.create_collections([{'name':name}])

    def create_collections(self, collections):
        """Parameters:
        - collections: must be a list of dictionaries with key "name"."""
        return self.request('collections/create', collections)

    def add_entities_to_collection(self, collectionId, entityIds):
        """Adds the given entities into a collection.
        
        Parameters:
        - collectionId: the collection ID string
        - entityIds: a list with entity ID strings"""
        return self.request('collections/addentities', {'collectionId':collectionId, 'entityIds':entityIds})

    def remove_entities_from_collection(self):
        """Removes the given entities from a collection.
        
        Parameters:
        - collectionId: the collection ID string
        - entityIds: a list with entity ID strings"""
        return self.request('collections/removeentities', {'collectionId':collectionId, 'entityIds':entityIds})

    def list_collections(self, collectionIds=None, minId=None):
        """Parameters:
        - collectionIds: a list with strings (no more than 256)
        - minId: for a contigous collections list starting from this ID"""
        params = {}

        if collectionIds:
            params['collectionIds'] = collectionIds

        if minId:
            params['minId'] = minId

        return self.request('collections/list', params)

    def delete_collections(self, collectionIds):
        """Parameters:
        - collectionIds: a list with strings"""
        return self.request('collections/delete', {'collectionIds':collectionIds})

    # Methods for Crumbs

    def format_crumb(self, crumb):
        if isinstance(crumb['timestamp'], datetime.datetime):
            timestamp = time.mktime(crumb['timestamp'].timetuple())
        elif isinstance(crumb['timestamp'], (float,int)):
            timestamp = crumb['timestamp']
        else:
            raise TypeError('Invalid timestamp: %s' % crumb['timestamp'])

        values = {
            'location': {'lat':float(crumb['location']['lat']), 'lng':float(crumb['location']['lng'])},
            'timestamp': timestamp,
            }

        if crumb.get('confidenceRadius',None) is not None:
            values['confidenceRadius'] = float(values['confidenceRadius'])
        if crumb.get('heading',None) is not None:
            values['heading'] = int(values['heading'])
        if isinstance(crumb.get('userData',None), dict):
            values['userData'] = values['userData']

        return values

    def record_crumb(self, entityId, location, timestamp, confidenceRadius=None, heading=None, userData=None):
        return self.record_crumbs(entityId, {
            'location':location,
            'timestamp':timestamp,
            'confidenceRadius':confidenceRadius,
            'heading':heading,
            'userData':userData,
            })

    def record_crumbs(self, entityId, crumbs):
        """Parameters:
        - entityId: an entity ID string
        - crumbs: a list with dictionaries with crumbs information
            - "location" (dict), "timestamp" (UTC), "confidenceRadius" (0~35000), "heading" (0~359) and "userData" (dict).
              https://developers.google.com/maps/documentation/business/tracks/crumbs#overview"""
        params = {'entityId':entityId, 'crumbs': map(self.format_crumb, crumbs)}
        return self.request('crumbs/record', params)

    def get_recent_crumbs(self):
        method = 'crumbs/getrecent'

    def get_crumbs_history(self):
        method = 'crumbs/gethistory'

    def summarize_crumbs(self):
        method = 'crumbs/summarize'

    def get_crumbs_location_info(self):
        method = 'crumbs/getlocationinfo'

    def delete_crumbs(self):
        method = 'crumbs/delete'

    # Methods for Geofences

    def create_geofences(self):
        method = 'geofences/create'

    def add_members_to_geofences(self):
        method = 'geofences/addmembers'

    def remove_members_from_geofences(self):
        method = 'geofences/removemembers'

    def list_geofences(self):
        method = 'geofences/list'

    def delete_geofences(self):
        method = 'geofences/delete'

    def get_active_geofences(self):
        method = 'geofences/getrecentlyactive'


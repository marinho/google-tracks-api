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

    def parse_timestamp(self, timestamp):
        if isinstance(crumb['timestamp'], datetime.datetime):
            return time.mktime(crumb['timestamp'].timetuple())
        elif isinstance(crumb['timestamp'], (float,int)):
            return crumb['timestamp']
        else:
            raise TypeError('Invalid timestamp: %s' % crumb['timestamp'])

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
        timestamp = self.parse_timestamp(crumb['timestamp'].timetuple())

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

    def get_recent_crumbs(self, collectionId):
        """Retrieves recent crumbs for the given collection.
        
        Parameters:
        - collectionId: the collection ID string"""
        return self.request('crumbs/getrecent', {'collectionId':collectionId})

    def get_crumbs_history(self, entityId, timestamp, countBefore=None, countAfter=None):
        """Returns until 512 crumbs for a given entity a period of time based on a given timestamp
        
        Parameters:
        - entityId: an entity ID string
        - timestamp: timestamp of interest
        - countBefore: optional (0~512)
        - countAfter: optional (0~512)"""

        params = {'entityId':entityId, 'timestamp': self.parse_timestamp(timestamp)}
        if countBefore is not None:
            params['countBefore'] = countBefore
        if countAfter is not None:
            params['countAfter'] = countAfter

        return self.request('crumbs/gethistory', params)

    def summarize_crumbs(self, entityId, minTimestamp, maxTimestamp):
        """Returns a summarized path for a given Entity between two timestamps
        
        Parameters:
        - entityId: an entity ID string
        - minTimestamp: start timestamp
        - maxTimestamp: end timestamp"""

        return self.request('crumbs/summarize', {
            'entityId': entityId,
            'minTimestamp': self.parse_timestamp(minTimestamp),
            'maxTimestamp': self.parse_timestamp(maxTimestamp),
            })

    def get_crumbs_location_info(self, entityId, timestamp, language=None):
        """Returns the location information for a given entity in a given timestamp
        
        Parameters:
        - entityId: an entity ID string
        - timestamp: timestamp of interest
        - language: optional (i.e. en, pt-BR, fr, etc.)"""

        params = {'entityId':entityId, 'timestamp': self.parse_timestamp(timestamp)}
        if language is not None:
            params['language'] = language

        return self.request('crumbs/getlocationinfo', params)

    def delete_crumbs(self, entityId, minTimestamp, maxTimestamp):
        """Deletes all crumbs for a given Entity between two timestamps
        
        Parameters:
        - entityId: an entity ID string
        - minTimestamp: start timestamp
        - maxTimestamp: end timestamp"""

        return self.request('crumbs/delete', {
            'entityId': entityId,
            'minTimestamp': self.parse_timestamp(minTimestamp),
            'maxTimestamp': self.parse_timestamp(maxTimestamp),
            })

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


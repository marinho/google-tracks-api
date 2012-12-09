# Copyright 2012 Google Inc. All Rights Reserved.
# Original: https://developers.google.com/maps/documentation/business/tracks/auth

"""Make a request to Tracks API.

Usage: make_request METHOD JSON_REQUEST_BODY
Example: make_request crumbs/getlocationinfo \
    "{entityId: '280415822391405995', timestamp: '1334643465000000'}"
"""

import time
import datetime
import sys
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials
import json

# Set up the email address of the service account and thepath to the private
# key. These values should be replaced with your own credentials.
try:
    from local_settings import *
except ImportError:
    CLIENT_EMAIL = None
    PRIVATE_KEY = None

now = time.mktime(datetime.datetime.utcnow().timetuple())

# Get the API method and request body from the command line arguments.
method = sys.argv[1]
#body = sys.argv[2] if len(sys.argv) > 2 else ''
if method == 'entities/create':
    body = json.dumps({'entities':[
        {'name':'Marios Vehicle', 'type':'AUTOMOBILE'}, # "a4783c6b63951bdd"
        {'name':'Tiagos Vehicle', 'type':'AUTOMOBILE'}, # "e489ec95b838c1fa"
        ]}) # TRUCK, WATERCRAFT, PERSON
elif method == 'entities/delete':
    body = json.dumps({'entityIds':["74437a1958483232","ec112841f2b7c744","f56cf27773d497ef"]})
elif method == 'collections/create':
    body = json.dumps({'collections':[
        {'name':'TDispatch Fleet'}, # "8d11d3be39af079e"
        ]})
elif method == 'collections/addentities':
    body = json.dumps({
        'collectionId': "8d11d3be39af079e",
        'entityIds': ["a4783c6b63951bdd","e489ec95b838c1fa"],
        })
elif method == 'crumbs/record':
    body = json.dumps({
        "crumbs": [
            {#"confidenceRadius": 3.14,
             "location": {"lat": 52.531602, "lng": 13.388297},
             "timestamp": now,
             "userData": {"driver_name": "Mario"}},
            {"location": {"lat": 52.531636, "lng": 13.388576},
             "timestamp": now + 10,
             "userData": {"driver_name": "Mario"}},
            {"location": {"lat": 52.531682, "lng": 13.388989},
             "timestamp": now + 20,
             "userData": {"driver_name": "Mario"}},
        ],
        "entityId": "a4783c6b63951bdd"
        })
elif method == 'crumbs/getrecent':
    body = json.dumps({'collectionId':"8d11d3be39af079e"})
elif method == 'crumbs/gethistory':
    body = json.dumps({
        "entityId": "a4783c6b63951bdd",
        "timestamp": now,
        "countBefore": 25,
        })
elif method == 'geofences/create':
    body = json.dumps({'geofences':[
        {'name':'Berlin Mitte',
         'polygon':{
             'invert':False,
             'loops':[
                 {'vertices':[
                     {'lat':52.532175, 'lng':13.387592},
                     {'lat':52.530693, 'lng':13.387731},
                     {'lat':52.530673, 'lng':13.390768},
                     {'lat':52.532553, 'lng':13.391787},
                     ]}
                 ],
             }},
        ]})
elif method == 'geofences/addmembers':
    body = json.dumps({
        'geofenceId':"b5f391030ac12c95",
        'collectionIds':['8d11d3be39af079e'],
        'entityIds':['a4783c6b63951bdd'],
        })
else:
    body = ''

# Load the key in PKCS 12 format that you downloaded from the Google API
# Console when you created your Service account.
f = file(PRIVATE_KEY, 'rb')
key = f.read()
f.close()

# Create an httplib2.Http object to handle our HTTP requests and authorize
# it with the Credentials. Note that the first parameter,
# service_account_name, is the Email address created for the Service
# account. It must be the email address associated with the key that was
# created.
credentials = SignedJwtAssertionCredentials(
    CLIENT_EMAIL,
    key,
    scope='https://www.googleapis.com/auth/tracks',
    token_uri='https://accounts.google.com/o/oauth2/token')
http = httplib2.Http()
http = credentials.authorize(http)

# Make the HTTP POST request to the Google Maps Tracks API.
url = "https://www.googleapis.com/tracks/v1/%s" % method
headers = {
    'content-type': 'application/json',
    'content-length': '%d' % len(body),
}
_, content = http.request(url, 'POST', headers=headers, body=body)

# Output response.
print content


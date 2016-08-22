
from google.appengine.ext import ndb

class Location(ndb.Model):
    country = ndb.StringProperty()
    region  = ndb.StringProperty()
    city    = ndb.StringProperty()
    geo     = ndb.GeoPtProperty(indexed=False)
    ipaddress = ndb.StringProperty('ip')

def from_request(req):
    headers = req.headers
    loc = Location(country=headers.get('X-AppEngine-Country'),
            region=headers.get('X-AppEngine-Region'),
            city=headers.get('X-AppEngine-City'))
    lat_lon = headers.get('X-AppEngine-CityLatLong', '').split(',')
    if len(lat_lon) == 2:
        loc.geo = ndb.GeoPt(lat_lon[0], lat_lon[1])

    if hasattr(req, 'remote_addr'):
        loc.ipaddress = req.remote_addr
    return loc

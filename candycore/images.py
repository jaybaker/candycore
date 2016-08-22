import logging
from logging import debug, info, warning, error
import base64
import StringIO

from google.appengine.api import images
from google.appengine.ext import ndb

import gaeutils

import utils
from location import Location

## models

class Gallery(ndb.Expando):
    """
    name is the key
    """
    name = ndb.StringProperty(required=True)

    @classmethod
    def by_name(cls, name):
        key = ndb.Key(cls, name)
        return key.get()

class Image(ndb.Expando):
    created    = ndb.DateTimeProperty(auto_now_add=True)
    gallery    = ndb.KeyProperty()
    bucketname = ndb.StringProperty()
    serve_url  = ndb.StringProperty()
    loc        = ndb.StructuredProperty(Location)

    @property
    def store_url(self):
        root = '//storage.googleapis.com'
        if self.serve_url.startswith('/_ah'):
            root = '/_ah/gcs'
        return root + self.bucketname

    @classmethod
    def for_gallery(cls, gallery_key, since=None):
        """ Returns the query. """
        query = cls.query(cls.gallery == gallery_key)
        if since:
            query = query.filter(cls.created >= since)
        query = query.order(-cls.created)
        return query

## save

def save(data, bucket=None, gallery='default', size=None, 
        mimetype='image/jpeg', encoded=True):
    gallery_key = ndb.Key(Gallery, gallery)
    if encoded:
        image_data = base64.b64decode(data)
    else:
        image_data = data
    stream = StringIO.StringIO(image_data)
    stream.stream = stream
    fname = utils.generate_key() + '.jpg'

    bucketname = utils.store_file(bucket, stream, 
            filename=fname, mimetype=mimetype, dev=gaeutils.App.dev)
    blobkey = utils.gs_blobkey(bucketname)
    serving_url = None
    try:
        serving_url = images.get_serving_url(blobkey, size=size)
    except images.TransformationError as e:
        serving_url = images.get_serving_url(blobkey, size=size) # retry on random transformation error
    img = Image(gallery=gallery_key, bucketname=bucketname, 
            serve_url=serving_url)
    return img

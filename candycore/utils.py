import logging
from logging import debug, info, error
import uuid
import base64

from google.appengine.api import urlfetch
from google.appengine.ext.ndb import blobstore

import cloudstorage as gcs

def generate_key():
    """
    generates a uuid, encodes it with base32 and strips it's padding.
    this reduces the string size from 32 to 26 chars.
    """
    return base64.b32encode(uuid.uuid4().bytes).strip('=').lower()

def store_file(bucket, datastream, filename=None, mimetype='image/jpeg', dev=False):
    if filename is None:
        filename = generate_key()
    fname = bucket + '/%s' % filename

    # write the file/data
    def store_it():
        gcs_file = gcs.open(fname, 'w', content_type=mimetype, 
                options={'x-goog-acl': 'public-read', 
                    'Cache-Control': 'public, max-age=31536000'})
        gcs_file.write(datastream.stream.read())
        gcs_file.close()

    try:
        store_it()
    except urlfetch.DeadlineExceededError:
        store_it()

    # get the url
    if dev:
        url = '/_ah/gcs%s' % fname
    else:
        url = '//storage.googleapis.com%s' % fname
    debug('stored resource %s with url: %s' % (fname, url))
    return fname

def gcs_reader(bucket):
    gcs_file = gcs.open(bucket)
    return gcs_file

def rm_file(bucketname):
    try:
        gcs.delete(bucketname)
    except gcs.NotFoundError:
        pass

def gs_blobkey(bucket):
    """
    Create a blob key from a gs bucket/file.
    """
    blobkey = blobstore.blobstore.create_gs_key('/gs%s' % bucket)
    return blobkey

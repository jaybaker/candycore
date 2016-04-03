from logging import debug, info, error

from google.appengine.api import urlfetch

import json

url = 'https://api.parse.com/1/push'

def push_notification(msg, channels=[], 
        app_id='', api_key=''):
    # setup the data
    data = dict(channels=channels, 
            data=dict(alert=msg, sound="fms.caf"))
    headers = {"X-Parse-Application-Id": "%s" % (app_id),
               "X-Parse-REST-API-Key": "%s" % (api_key),
               "Content-Type": "application/json"}

    # convenience function
    def fetch():
        return urlfetch.fetch(url=url, payload=json.dumps(data), 
                headers=headers, method=urlfetch.POST, deadline=30)

    # send push notification
    try:
        resp = fetch()
    except:
        # retry once
        debug('retrying push')
        resp = fetch()

    if resp.status_code != 200:
        debug('status code: %s' % resp.status_code)
        debug('content: %s' % resp.content)
        debug('headers: %s' % resp.headers)
        error('failed to send parse notification')

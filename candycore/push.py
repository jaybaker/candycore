from logging import debug, info, error

from google.appengine.api import urlfetch

import json

PARSE_URL = 'https://api.parse.com/1/push'
FBASE_URL = 'https://fcm.googleapis.com/fcm/send'

def notify(topic, msg, key, priority='high'):
    headers = {"Authorization": "key=%s" % key,
               "Content-Type": "application/json"}

    to = '/topics/%s' % topic
    data = dict(to=to, priority=priority,
            notification=dict(body=msg))

    # convenience function
    def fetch():
        return urlfetch.fetch(url=FBASE_URL, payload=json.dumps(data), 
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
        error('failed to send push notification')

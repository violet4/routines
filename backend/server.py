#!/usr/bin/env python3
"""
"""
import datetime
import os
import json

import requests

import falcon


class ActivityResource:
    def on_get(self, req, resp):
        # resp.content_type = falcon.MEDIA_TEXT
        resp.content_type = falcon.MEDIA_JSON
        resp.text = json.dumps({'a': 1})


class OccurrenceResource:
    def on_get(self, req, resp):
        resp.content_type = falcon.MEDIA_JSON
        resp.text = json.dumps({'a': 1})


prefix = '/api'
# prefix = ''
app = falcon.App()
app.add_route(prefix+'/currency', CurrencyResource())
app.add_static_route('/', os.path.abspath('frontend/build'))
app.add_route(prefix+'/activity', ActivityResource())
app.add_route(prefix+'/occurrence', OccurrenceResource())

if __name__ == '__main__':
    pass

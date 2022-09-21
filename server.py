#!/usr/bin/env python3
"""
"""
import datetime
import os
import json

import requests

import falcon


class CurrencyResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        # resp.content_type = falcon.MEDIA_TEXT
        # resp.media = get_currency_values()


prefix = '/api'
# prefix = ''
app = falcon.App()
app.add_route(prefix+'/currency', CurrencyResource())
print(os.listdir(os.path.abspath('frontend/build')))
app.add_static_route('/', os.path.abspath('frontend/build'))

if __name__ == '__main__':
    pass

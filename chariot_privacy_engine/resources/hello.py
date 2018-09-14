# -*- coding: utf-8 -*-

import json
import falcon


class HelloWorldResource(object):
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def on_get(self, req, resp):
        self.mqtt.publish('house/light', 'ON')
        doc = {
            'images': [
                {
                    'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
                }
            ]
        }
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        resp.body = json.dumps(doc, ensure_ascii=False)

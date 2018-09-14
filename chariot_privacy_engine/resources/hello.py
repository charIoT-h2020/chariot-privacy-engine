# -*- coding: utf-8 -*-

import json
import falcon


class HelloWorldResource(object):
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def on_post(self, req, resp):
        message_req = req.context['data']

        if message_req:
            self.mqtt.publish('temperature/%s' % message_req['id'], message_req['value'])

        doc = {
            'status': 0
        }
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        resp.body = json.dumps(doc, ensure_ascii=False)

# -*- coding: utf-8 -*-


class HelloWorldResource(object):
    def __init__(self, mqtt):
        self.mqtt = mqtt

    def on_post(self, req, resp):
        id = req.get_json('id')
        value = req.get_json('value')

        self.mqtt.publish('temperature/%s' % id, value)

        resp.json = {
            'status': 0,
            'msg': [id, value]
        }

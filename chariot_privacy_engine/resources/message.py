# -*- coding: utf-8 -*-


class MessageResource(object):
    def __init__(self, engine):
        self.engine = engine

    def on_post(self, req, resp):
        sensor_id = req.get_json('id')
        value = req.get_json('value')
        print("log: ", sensor_id, value)
        self.engine.publish('temperature/%s' % sensor_id, value)

        resp.json = {
            'status': 0,
            'msg': [sensor_id, value]
        }

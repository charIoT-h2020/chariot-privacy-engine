# -*- coding: utf-8 -*-


class MessageResource(object):
    def __init__(self, engine):
        self.engine = engine

    def on_post(self, req, resp):
        sensor_id = req.get_json('id')
        value = req.get_json('value')

        resp.json = self.engine.apply({
            id: sensor_id,
            value: value
        })

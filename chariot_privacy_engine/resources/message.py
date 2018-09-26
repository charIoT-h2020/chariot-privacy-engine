# -*- coding: utf-8 -*-
from chariot_privacy_engine.engine import Message


class MessageResource(object):
    def __init__(self, engine):
        self.engine = engine

    def on_post(self, req, resp):
        sensor_id = req.get_json('id')
        value = req.get_json('value')
        destination = req.get_json('destination')

        resp.json = self.engine.apply(Message(sensor_id, value, destination))

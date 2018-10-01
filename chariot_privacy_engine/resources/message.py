# -*- coding: utf-8 -*-
from ..model import Message


class MessageResource(object):
    def __init__(self, engine):
        self.engine = engine

    def on_post(self, req, resp):
        sensor_id = req.get_json('sensor_id')
        value = req.get_json('value')

        resp.json = self.engine.apply(Message(sensor_id, value))

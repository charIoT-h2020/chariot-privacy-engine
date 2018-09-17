# -*- coding: utf-8 -*-


class Message(object):
    def __init__(self, sensor_id, value):
        self.id = sensor_id
        self.value = value

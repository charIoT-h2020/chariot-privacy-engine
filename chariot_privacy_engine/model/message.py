# -*- coding: utf-8 -*-


class Message(object):
    def __init__(self, sensor_id, value, destination):
        self.id = sensor_id
        self.value = value
        self.destination = destination

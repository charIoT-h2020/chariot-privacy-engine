# -*- coding: utf-8 -*-
from iotl import interpreter
from chariot_base.model import Alert


class TopologyInspector(object):
    def __init__(self, engine):
        self.human_name = "topology_inspector"
        self.engine = engine

    def check(self, message):
        if self.engine.iotl.isSensitive(message.sensor_id) == 0:
            msg = 'Sensor \'%s\' returns sensitive information' % message.sensor_id
            self.engine.raise_alert(Alert(self.human_name, msg, 50))

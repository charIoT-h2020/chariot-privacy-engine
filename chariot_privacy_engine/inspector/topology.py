# -*- coding: utf-8 -*-
import logging

from iotl import interpreter
from chariot_base.model import Alert


class TopologyInspector(object):
    def __init__(self, engine):
        self.human_name = "topology_inspector"
        self.engine = engine

    def check(self, message, span):
        if self.engine.is_sensitive(span, message) == True:
            msg = 'Sensor \'%s\' returns sensitive information' % message.sensor_id
            alert = Alert(self.human_name, msg, 50)
            alert.sensor_id = message.sensor_id
            self.engine.raise_alert(alert, span)

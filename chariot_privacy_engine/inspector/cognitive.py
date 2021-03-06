# -*- coding: utf-8 -*-
import json
from chariot_base.model import Alert


class CognitiveInspector(object):
    def __init__(self, engine):
        self.human_name = "cognitive_inspector"
        self.engine = engine

    def check(self, message, span):
        self.engine.save_instance(span, message)

        if message.value == 'AB00110':
            msg = 'Sensor %s returns sensitive information' % message.sensor_id
            self.engine.raise_alert(Alert(self.human_name, msg, 100), span)

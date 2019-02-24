# -*- coding: utf-8 -*-
from iotl import interpreter
from chariot_base.model import Alert


class TopologyInspector(object):
    def __init__(self, engine):
        self.human_name = "topology_inspector"
        self.engine = engine
        self.IoTState = interpreter.IoTState()
        self.IoTState.parse('define SENSOR temp --params { "privacySensitive": 0 }')

    def check(self, message):
        print(self.IoTState.params)
        if self.IoTState.params['temp']['privacySensitive'] == 0:
            print("Test")
            msg = 'Sensor %s returns sensitive information' % message.sensor_id
            self.engine.raise_alert(Alert(msg, 50))

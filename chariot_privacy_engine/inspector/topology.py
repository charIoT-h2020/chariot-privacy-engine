# -*- coding: utf-8 -*-
from chariot_base.model import Alert


class TopologyInspector(object):
    def __init__(self, engine):
        self.engine = engine
        self.topology = {
            'urn:ngsi-ld:temp:001': {
                'sensitive': False
            },
            'urn:ngsi-ld:card:001': {
                'sensitive': True
            }
        }

    def check(self, message):
        if self.topology[message.sensor_id]['sensitive']:
            msg = 'Sensor %s returns sensitive information' % message.sensor_id
            self.engine.raise_alert(Alert(msg, 50))

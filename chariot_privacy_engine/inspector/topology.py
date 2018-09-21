# -*- coding: utf-8 -*-
from .alert import Alert


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
        if self.topology[message.id]['sensitive']:
            msg = 'Sensor %s returns sensitive information' % message.id
            self.engine.raise_alert(Alert(msg, 50))

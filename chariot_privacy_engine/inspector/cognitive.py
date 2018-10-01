# -*- coding: utf-8 -*-
from ..model import Alert


class CognitiveInspector(object):
    def __init__(self, engine):
        self.engine = engine

    def check(self, message):
        if message.value == 'AB00110':
            msg = 'Sensor %s returns sensitive information' % message.id
            self.engine.raise_alert(Alert(msg, 100))

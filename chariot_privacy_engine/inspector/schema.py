# -*- coding: utf-8 -*-
import logging

from chariot_base.model import Alert


class SchemaInspector(object):
    SEVERITY = 50

    def __init__(self, engine):
        self.human_name = "schema_inspector"
        self.engine = engine

    def check(self, message, span):
        sid = message.sensor_id
        for schema in self.engine.schema: 
            if self.engine.is_match(span, schema, message) == True:
                if sid not in schema['sensors']:
                    msg = f'Sensor\'s \'{sid}\' payload matches private schema \'{schema["pattern"]}\''
                    alert = Alert(self.human_name, msg, SchemaInspector.SEVERITY)
                    alert.sensor_id = sid
                    self.engine.raise_alert(alert, span)

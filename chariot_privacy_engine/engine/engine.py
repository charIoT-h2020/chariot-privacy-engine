# -*- coding: utf-8 -*-
import logging
import json

from ..filter import RsaRuleFilter
from ..inspector import CognitiveInspector, TopologyInspector

from chariot_base.utilities import Traceable
from chariot_base.utilities.iotlwrap import IoTLWrapper


class Engine(Traceable):
    def __init__(self):
        self.tracer = None
        self.southbound = None
        self.northbound = None

        self.iotl = None

        self.inspectors = [
            CognitiveInspector(self),
            TopologyInspector(self)
        ]

        self.filters = [
            RsaRuleFilter(self)
        ]

    def inject(self, southbound, northbound):
        self.southbound = southbound
        self.northbound = northbound

    def start(self):
        self.subscribe_to_southbound()
        self.subscribe_to_northbound()

    def inject_iotl(self, iotl):
        self.iotl = iotl

    def subscribe_to_southbound(self):
        self.southbound.subscribe('privacy/#', qos=0)

    def subscribe_to_northbound(self):
        pass

    def apply(self, message, child_span):
        span = self.start_span('apply', child_span)
        self.filter(message, span)
        self.inspect(message, span)
        self.close_span(span)
        return 0

    def inspect(self, message, child_span):
        for _inspector in self.inspectors:
            span = self.start_span('filter_%s' % _inspector.human_name, child_span)
            _inspector.check(message, span)
            self.close_span(span)

    def filter(self, message, child_span):
        for _filter in self.filters:
            span = self.start_span('filter_%s' % _filter.human_name, child_span)
            _filter.do(message, span)
            self.close_span(span)

    def publish(self, message, span):
        m = self.inject_to_message(span, message.dict())
        self.southbound.publish('northbound', json.dumps(m))

    def raise_alert(self, alert, span):
        m = json.dumps(self.inject_to_message(span, alert.dict()))
        logging.debug(m)
        self.northbound.publish('alerts', m)

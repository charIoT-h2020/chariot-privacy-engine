# -*- coding: utf-8 -*-
from ..filter import RsaRuleFilter
from ..inspector import CognitiveInspector, TopologyInspector


class Engine(object):
    def __init__(self):
        self.southbound = None
        self.northbound = None

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

    def subscribe_to_southbound(self):
        self.southbound.subscribe('privacy/#', qos=0)

    def subscribe_to_northbound(self):
        pass

    def apply(self, message):
        self.filter(message)
        self.inspect(message)
        return 0

    def inspect(self, message):
        for _inspector in self.inspectors:
            _inspector.check(message)

    def filter(self, message):
        for _filter in self.filters:
            _filter.do(message)

    def publish(self, message):
        self.southbound.publish('northbound', str(message))

    def raise_alert(self, alert):
        self.northbound.publish('alerts', str(alert))

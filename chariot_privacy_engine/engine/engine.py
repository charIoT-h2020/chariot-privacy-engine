# -*- coding: utf-8 -*-
from ..filter import RsaRuleFilter
from ..inspector import CognitiveInspector, TopologyInspector


class Engine(object):
    def __init__(self, southbound, northbound):
        self.southbound = southbound
        self.northbound = northbound

        self.inspectors = [
            CognitiveInspector(self),
            TopologyInspector(self)
        ]

        self.filters = [
            RsaRuleFilter(self)
        ]

        self.subscribe_to_southbound()
        self.subscribe_to_northbound()

    def subscribe_to_southbound(self):
        self.southbound.subscribe([
            ('privacy/#', 0)
        ])

    def subscribe_to_northbound(self):
        pass

    def apply(self, message):
        self.filter(message)
        self.inspect(message)
        return 0

    def inspect(self, message):
        for inspector in self.inspectors:
            print('Run inspection: %s' % inspector.__class__.__name__)
            inspector.check(message)

    def filter(self, message):
        for _filter in self.filters:
            _filter.do(message)

    def publish(self, message):
        self.northbound.publish('%s/%s' % (message.destination, message.id), message.value)

    def raise_alert(self, alert):
        self.northbound.publish('alerts', str(alert))

    def on_message(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    def on_log(self, client, userdata, level, buf):
        print("log: ", buf)

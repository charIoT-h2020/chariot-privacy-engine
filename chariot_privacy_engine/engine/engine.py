# -*- coding: utf-8 -*-
from ..inspector import CognitiveInspector, TopologyInspector


class Engine(object):
    def __init__(self, client):
        self.client = client

        self.inspectors = [
            CognitiveInspector(self),
            TopologyInspector(self)
        ]

    def subscribe_to_southbound(self):
        self.client.subscribe('northbound/dashboard/alerts')

    def apply(self, message):
        self.client.publish('northbound/temperature/%s' % message.id, message.value)
        self.inspect(message)
        return 0

    def inspect(self, message):
        for inspector in self.inspectors:
            print('Run inspection: %s' % inspector.__class__.__name__)
            inspector.check(message)

    def raise_alert(self, alert):
        self.client.publish('northbound/dashboard/alerts', '%s,%s' % (alert.msg, alert.severity))

    @staticmethod
    def on_message(client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    @staticmethod
    def on_log(client, userdata, level, buf):
        print("log: ", buf)

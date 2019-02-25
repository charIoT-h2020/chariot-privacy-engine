# -*- coding: utf-8 -*-
from ..filter import RsaRuleFilter
from ..inspector import CognitiveInspector, TopologyInspector

from chariot_base.utilities import Tracer


class Engine(object):
    def __init__(self):
        self.tracer = None
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

    def inject_tracer(self, tracer):
        self.tracer = tracer

    def set_up_tracer(self, options):
        self.tracer = Tracer(options)
        self.tracer.init_tracer()

    def start_span(self, id, child_span=None):
        if self.tracer is None:
            return

        if child_span is None:
            return self.tracer.tracer.start_span(id)
        else:
            return self.tracer.tracer.start_span(id, child_of=child_span)

    def close_span(self, span):
        if self.tracer is None:
            return
        span.finish()

    def inject_tracer(self, tracer):
        self.tracer = tracer

    def set_up_tracer(self, options):
        self.tracer = Tracer(options)
        self.tracer.init_tracer()

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
            _inspector.check(message)
            self.close_span(span)

    def filter(self, message, child_span):
        for _filter in self.filters:
            span = self.start_span('filter_%s' % _filter.human_name, child_span)
            _filter.do(message)
            self.close_span(span)

    def publish(self, message):
        self.southbound.publish('northbound', str(message))

    def raise_alert(self, alert):
        self.northbound.publish('alerts', str(alert))

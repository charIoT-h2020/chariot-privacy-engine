# -*- coding: utf-8 -*-
import logging
import json
import requests

from ..filter import RsaRuleFilter
from ..inspector import CognitiveInspector, TopologyInspector, SchemaInspector

from chariot_base.utilities import Traceable
from chariot_base.utilities.iotlwrap import IoTLWrapper

from datetime import datetime, timedelta

class Engine(Traceable):
    def __init__(self, options={}):
        self.tracer = None
        self.southbound = None
        self.northbound = None
        self.schema = []

        self.iotl = None
        self.session = requests.Session()
        self.session.trust_env = False
        self.options = options
        self.last_sync_datetime = None

        self.inspectors = [
            CognitiveInspector(self),
            TopologyInspector(self),
            SchemaInspector(self)
        ]
        self.filters = [
            RsaRuleFilter(self)
        ]

        self.prepare_global_mute_options()

    def inject(self, southbound, northbound):
        self.southbound = southbound
        self.northbound = northbound

    def start(self):
        self.subscribe_to_southbound()
        self.subscribe_to_northbound()

    def inject_iotl(self, iotl):
        self.iotl = iotl

    def set_up_iotl_url(self, iotl_url):
        self.iotl_url = iotl_url

    def subscribe_to_southbound(self):
        self.southbound.subscribe_to_topics()

    def subscribe_to_northbound(self):
        pass

    def apply(self, message, child_span):
        span = self.start_span('apply', child_span)
        self.sync_iotl(span)
        self.filter(message, span)
        self.inspect(message, span)
        self.close_span(span)
        return 0

    def inspect(self, message, child_span):
        for _inspector in self.inspectors:
            if self.is_not_muted(_inspector.human_name):
                if self.is_not_muted_for_sensor(_inspector.human_name, message):
                    span = self.start_span(f'filter_{_inspector.human_name}', child_span)
                    _inspector.check(message, span)
                    self.close_span(span)
                else:
                    logging.debug(f'Rule {_inspector.human_name} is muted for sensor "{message.sensor_id}"')
            else:
                logging.debug(f'Rule {_inspector.human_name} is muted')

    def filter(self, message, child_span):
        for _filter in self.filters:
            if self.is_not_muted(_filter.human_name):
                if self.is_not_muted_for_sensor(_filter.human_name, message):
                    span = self.start_span(f'filter_{_filter.human_name}', child_span)
                    _filter.do(message, span)
                    self.close_span(span)
                else:
                    logging.debug(f'Rule {_filter.human_name} is muted for sensor "{message.sensor_id}"')
            else:
                logging.debug(f'Rule {_filter.human_name} is muted')

    def publish(self, message, span):
        m = self.inject_to_message(span, message.dict())        
        self.southbound.publish('northbound', json.dumps(m))
        logging.debug(f'Publish message from "{message.sensor_id}" to "{message.destination}"')

    def raise_alert(self, alert, span):
        m = json.dumps(self.inject_to_message(span, alert.dict()))
        logging.debug(m)
        self.northbound.publish('alerts', m)

    def get_acl(self, span, message):
        return self.iotl.acl(message.sensor_id)

    def get_params(self, span, destination):
        return self.iotl.params(destination)

    def is_sensitive(self, span, message):
        return self.iotl.isSensitive(message.sensor_id)

    def is_match(self, span, schema, message):
        return self.iotl.is_match(schema, message.value)

    def sync_iotl(self, span):
        if self.iotl_url is None:
            return
        
        if self.should_sync_iotl():
            logging.debug('Sync topology')
            url = self.iotl_url
            headers = self.inject_to_request_header(span, url)
            self.set_tag(span, 'url', url)
            result = self.session.get(url, headers=headers)
            current_iotl = result.json()
            self.iotl.load(current_iotl['code'])
            self.schema = self.iotl.schema(True)

            self.last_sync_datetime = datetime.now()

    def should_sync_iotl(self):
        if self.last_sync_datetime is None:
            return True
        return datetime.now() - self.last_sync_datetime >= timedelta(seconds=self.options.get('iotl_sync_delay', 60))

    def is_not_muted(self, id):
        return not self.muted_options[id]

    def is_not_muted_for_sensor(self, id, message):
        muted = self.iotl.params(message.sensor_id).get('mute', {})
        return muted.get(id, 0) == 0

    def prepare_global_mute_options(self):
        self.muted_options = self.options.get('mute', {})
        for _inspector in self.inspectors:
            if _inspector.human_name not in self.muted_options:
                self.muted_options[_inspector.human_name] = False
        for _filters in self.filters:
            if _filters.human_name not in self.muted_options:
                self.muted_options[_filters.human_name] = False
# -*- coding: utf-8 -*-

import os
import uuid
import json
import gmqtt
import asyncio
import signal
import logging

from chariot_privacy_engine import __service_name__
from chariot_privacy_engine.resources import MessageResource
from chariot_privacy_engine.engine import Engine
from chariot_base.model import Message
from chariot_base.utilities import open_config_file, HealthCheck
from chariot_base.utilities.iotlwrap import IoTLWrapper
from chariot_base.connector import LocalConnector, create_client


class SouthboundConnector(LocalConnector):
    def __init__(self, options):
        super(SouthboundConnector, self).__init__()
        self.engine = None

        if 'health' in options:
            logging.info('Enabling health checks endpoints')
            self.health = HealthCheck(options['name']).inject_connector(self)
            self.healthTopic = options['health']['endpoint']

    def on_message(self, client, topic, payload, qos, properties):
        if topic == self.healthTopic:
            self.health.do(payload)
            return

        msg = payload.decode('utf-8')
        deserialized_model = json.loads(msg)
        span = self.start_span_from_message('on_message', deserialized_model)

        try:
            sensor_id = deserialized_model['sensor_id']
            value = json.dumps(deserialized_model['value'])
            message = Message(sensor_id, value)
            message.id = deserialized_model['package_id']

            logging.debug('Received packet "%s" from "%s"' %
                        (message.id, sensor_id))
            self.engine.apply(message, span)
            self.close_span(span)
        except Exception as ex:
            logging.error(ex)
            self.set_tag(span, 'is_ok', False)
            self.error(span, ex, False)
            self.close_span(span)

    def set_up_engine(self, engine):
        self.engine = engine


class NorthboundConnector(LocalConnector):
    def __init__(self, options):
        super(NorthboundConnector, self).__init__()
        self.engine = None

    def set_up_engine(self, engine):
        self.engine = engine


STOP = asyncio.Event()


def ask_exit(*args):
    logging.info('Stoping....')
    STOP.set()


async def main(args=None):
    engine = Engine()

    opts = open_config_file()

    options_engine = opts.privacy_engine
    options_tracer = opts.tracer
    options_topology = opts.topology

    ioTLWrapper = IoTLWrapper(options_topology)
    ioTLWrapper.load()
    
    if options_tracer['enabled'] is True:
        options_tracer['service'] = __service_name__
        logging.info(f'Enabling tracing for service "{__service_name__}"')
        engine.set_up_tracer(options_tracer)

    engine.inject_iotl(ioTLWrapper)
    engine.set_up_iotl_url(options_topology['iotl_url'])

    southbound = SouthboundConnector(options_engine)
    southbound.set_up_engine(engine)
    southbound.inject_tracer(engine.tracer)
    client_south = await create_client(opts.brokers.southbound)
    southbound.register_for_client(client_south)

    northbound = NorthboundConnector(options_engine)
    northbound.set_up_engine(engine)
    northbound.inject_tracer(engine.tracer)
    client_north = await create_client(opts.brokers.northbound)
    northbound.register_for_client(client_north)

    engine.inject(southbound, northbound)
    engine.start()

    logging.info('Waiting message from Southbound Dispatcher')
    await STOP.wait()
    await client_south.disconnect()
    await client_north.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
    logging.info('Stopped....')

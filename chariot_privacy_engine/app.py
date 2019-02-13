# -*- coding: utf-8 -*-

import os
import uuid
import json
import gmqtt
import asyncio
import signal

import falcon
import falcon_jsonify

from chariot_privacy_engine.resources import MessageResource
from chariot_privacy_engine.engine import Engine
from chariot_base.model import Message
from chariot_base.utilities import open_config_file
from chariot_base.connector import LocalConnector, create_client


class SouthboundConnector(LocalConnector):
    def __init__(self, options):
        super(SouthboundConnector, self).__init__()
        self.engine = None

    def on_message(self, client, topic, payload, qos, properties):
        span = self.start_span('on_message')
        msg = payload.decode('utf-8')
        deserialized_model = json.loads(msg)
        sensor_id = deserialized_model['sensor_id']
        value = json.dumps(deserialized_model['value'])
        self.engine.apply(Message(sensor_id, value), span)
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
    print('Stoping....')
    STOP.set()


async def main(args=None):
    engine = Engine()

    opts = open_config_file()

    options_engine = opts['privacy_engine']
    options_tracer = opts['tracer']

    engine.set_up_tracer(options_tracer)

    southbound = SouthboundConnector(options_engine)
    southbound.set_up_engine(engine)
    southbound.inject_tracer(engine.tracer)
    client_south = await create_client(opts['brokers']['southbound'])
    southbound.register_for_client(client_south)

    northbound = NorthboundConnector(options_engine)
    northbound.set_up_engine(engine)
    northbound.inject_tracer(engine.tracer)
    client_north = await create_client( opts['brokers']['northbound'])
    northbound.register_for_client(client_north)

    engine.inject(southbound, northbound)
    engine.start()

    # app = falcon.API(middleware=[
    #     falcon_jsonify.Middleware(help_messages=True),
    # ])
    #
    # message = MessageResource(engine)
    #
    # app.add_route('/message', message)

    print('Waiting message from Southbound Dispatcher')
    await STOP.wait()
    await client_south.disconnect()
    await client_north.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
    print('Stopped....')
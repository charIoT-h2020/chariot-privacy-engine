# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
import uuid
import json
import gmqtt
import asyncio
import signal

import uuid
import json
import falcon
import falcon_jsonify

from chariot_privacy_engine.resources import MessageResource
from chariot_privacy_engine.engine import Engine
from chariot_base.model import Message, DataPointFactory
from chariot_base.connector import LocalConnector


class SouthboundConnector(LocalConnector):
    def __init__(self, options):
        super(SouthboundConnector, self).__init__()
        self.engine = None
        self.connector = None
        self.point_factory = DataPointFactory(options['database'], options['table'])

    def on_message(self, client, topic, payload, qos, properties):
        point = self.to_data_point(payload, topic)

    def set_up_engine(self, engine):
        self.engine = engine


class NorthboundConnector(LocalConnector):
    def __init__(self, options):
        super(NorthboundConnector, self).__init__()
        self.engine = None
        self.connector = None
        self.point_factory = DataPointFactory(options['database'], options['table'])

    def set_up_engine(self, engine):
        self.engine = engine


STOP = asyncio.Event()


def ask_exit(*args):
    STOP.set()


async def main(args=None):
    engine = Engine()

    filename = None
    for name in ['./config.json', './tests/config.json']:
        if os.path.isfile(name):
            filename = name

    if filename is None:
        raise Exception('Configuration file is not exists')

    with open('./tests/config.json', 'r') as read_file:
        opts = json.load(read_file)

    options_engine = opts['engine']['privacy']

    southbound = SouthboundConnector(options_engine)
    southbound.set_up_engine(engine)

    northbound = NorthboundConnector(options_engine)
    northbound.set_up_engine(engine)

    engine.inject(southbound, northbound)
    engine.start()

    # app = falcon.API(middleware=[
    #     falcon_jsonify.Middleware(help_messages=True),
    # ])
    #
    # message = MessageResource(engine)
    #
    # app.add_route('/message', message)

    await STOP.wait()
    await client_south.disconnect()
    await client_north.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())

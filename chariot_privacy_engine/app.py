# -*- coding: utf-8 -*-
import uuid
import falcon
import falcon_jsonify

from chariot_privacy_engine.resources import MessageResource
from chariot_privacy_engine.engine import Engine
from chariot_base.connector.local import LocalConnector


def main():
    # Initialize connection to southbound
    southbound = LocalConnector('southbound_%s' % uuid.uuid4(), '172.18.1.2')
    southbound.start(True)

    # Initialize connection to northbound
    northbound = LocalConnector('northbound_%s' % uuid.uuid4(), '172.18.1.3')
    northbound.start(True)

    engine = Engine(southbound, northbound)

    northbound.on_log = engine.on_log
    northbound.on_message = engine.on_message

    southbound.on_log = engine.on_log
    southbound.on_message = engine.on_message

    app = falcon.API(middleware=[
        falcon_jsonify.Middleware(help_messages=True),
    ])

    message = MessageResource(engine)

    app.add_route('/message', message)

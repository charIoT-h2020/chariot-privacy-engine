# -*- coding: utf-8 -*-

import falcon
import falcon_jsonify

import paho.mqtt.client as mqtt

from .resources import MessageResource
from .engine import Engine

# Initialize connection to southbound
southbound = mqtt.Client('southbound')
southbound.connect('172.18.1.2')
southbound.loop_start()

# Initialize connection to northbound
northbound = mqtt.Client('northbound')
northbound.connect('172.18.1.3')
northbound.loop_start()

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

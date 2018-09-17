# -*- coding: utf-8 -*-

import falcon
import falcon_jsonify

import paho.mqtt.client as mqtt

from .resources import MessageResource
from .engine import Engine

client = mqtt.Client('privacy_engine')
client.connect('127.0.0.1')
client.loop_start()

engine = Engine(client)
client.on_log = engine.on_log

engine.subscribe_to_southbound()
client.on_message = engine.on_message

app = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
])

message = MessageResource(engine)

app.add_route('/message', message)

# -*- coding: utf-8 -*-

import falcon
import falcon_jsonify

import paho.mqtt.client as mqtt

from .resources import HelloWorldResource


def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)


def on_log(client, userdata, level, buf):
    print("log: ", buf)


client = mqtt.Client('privacy_engine')
client.connect('127.0.0.1')

client.loop_start()
client.subscribe('temperature/#')

client.on_message = on_message
client.on_log = on_log

app = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
])

things = HelloWorldResource(client)

app.add_route('/things', things)

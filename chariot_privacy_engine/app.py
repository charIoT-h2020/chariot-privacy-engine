# -*- coding: utf-8 -*-

import falcon

import paho.mqtt.client as mqtt

from .resources import HelloWorldResource


def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)


client = mqtt.Client('privacy_engine')
client.connect('127.0.0.1')

client.loop_start()
client.subscribe('house/light')

client.on_message = on_message

app = falcon.API()

things = HelloWorldResource(client)

app.add_route('/things', things)

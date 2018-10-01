# -*- coding: utf-8 -*-
import uuid
import falcon
import falcon_jsonify

from chariot_privacy_engine.resources import MessageResource
from chariot_privacy_engine.engine import Engine
from chariot_base.connector.local import LocalConnector


class SouthboundConnector(LocalConnector):
    def on_message(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    def on_log(self, client, userdata, level, buf):
        print("log: ", buf)


class NorthboundConnector(LocalConnector):
    def on_message(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

    def on_log(self, client, userdata, level, buf):
        print("log: ", buf)


# Initialize connection to southbound
southbound = SouthboundConnector('southbound_%s' % uuid.uuid4(), '172.18.1.2')
southbound.start(False)

# Initialize connection to northbound
northbound = NorthboundConnector('northbound_%s' % uuid.uuid4(), '172.18.1.3')
northbound.start(False)

engine = Engine(southbound, northbound)

app = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
])

message = MessageResource(engine)

app.add_route('/message', message)

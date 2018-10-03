# -*- coding: utf-8 -*-
import uuid
import json
import falcon
import falcon_jsonify

from chariot_privacy_engine.resources import MessageResource
from chariot_privacy_engine.engine import Engine
from chariot_base.model import Message
from chariot_base.connector import LocalConnector


class SouthboundConnector(LocalConnector):
    def __init__(self, client_od, broker, controller):
        super().__init__(client_od, broker)
        self.engine = controller

    def on_message(self, client, userdata, message):
        deserialized_model = json.loads(str(message.payload.decode("utf-8")))
        sensor_id = deserialized_model['sensor_id']
        value = json.dumps(deserialized_model['value'])
        self.engine.apply(Message(sensor_id, value))

    def on_log(self, client, userdata, level, buf):
        print("log[%s]: %s" % (level, buf))


class NorthboundConnector(LocalConnector):
    def on_log(self, client, userdata, level, buf):
        print("log[%s]: %s" % (level, buf))


engine = Engine()

southbound = SouthboundConnector('southbound_%s' % uuid.uuid4(), '172.18.1.2', engine)
northbound = NorthboundConnector('northbound_%s' % uuid.uuid4(), '172.18.1.3')

engine.inject(southbound, northbound)
engine.start()

app = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
])

message = MessageResource(engine)

app.add_route('/message', message)

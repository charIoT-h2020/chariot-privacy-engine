# -*- coding: utf-8 -*-

import falcon
import falcon_jsonify

from .resources import MessageResource
from .engine import Engine, Client

# Initialize connection to southbound
southbound = Client('southbound', '172.18.1.2')
southbound.start(False)

# Initialize connection to northbound
northbound = Client('northbound', '172.18.1.3')
northbound.start(False)

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

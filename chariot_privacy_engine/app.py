# -*- coding: utf-8 -*-

import falcon

from .resources import HelloWorldResource

app = falcon.API()

things = HelloWorldResource()

app.add_route('/things', things)

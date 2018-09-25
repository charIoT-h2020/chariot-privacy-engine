# -*- coding: utf-8 -*-
import json
import datetime
from enum import Enum


class Alert(object):

    def __init__(self, msg=None, severity=100):
        self.timestamp = datetime.datetime.now().isoformat()
        self.msg = msg
        self.severity = severity

    def __str__(self):
        return json.dumps(self)

    def __unicode__(self):
        return json.dumps(self)

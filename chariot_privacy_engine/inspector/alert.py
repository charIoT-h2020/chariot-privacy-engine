# -*- coding: utf-8 -*-
import json
import datetime


class Alert(object):

    def __init__(self, msg=None, severity=100):
        self.timestamp = datetime.datetime.now().isoformat()
        self.msg = msg
        self.severity = severity

    def __str__(self):
        return json.dumps(self)

    def __unicode__(self):
        msg = {
            'msg': self.msg,
            'severity': self.severity
        }

        return json.dumps(msg)

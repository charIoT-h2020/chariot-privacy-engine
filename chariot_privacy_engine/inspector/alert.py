# -*- coding: utf-8 -*-
import datetime
from enum import Enum


class Alert(object):

    def __init__(self, msg=None, severity=100):
        self.timestamp = datetime.datetime.now().isoformat()
        self.msg = msg
        self.severity = severity

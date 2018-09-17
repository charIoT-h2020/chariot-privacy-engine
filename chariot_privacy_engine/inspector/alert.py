# -*- coding: utf-8 -*-
import datetime
from enum import Enum


class Severity(Enum):
    info = 0
    warning = 1
    critical = 2


class Alert(object):

    def __init__(self, msg=None, severity=Severity.critical):
        self.timestamp = datetime.datetime.now().isoformat()
        self.msg = msg
        self.severity = severity

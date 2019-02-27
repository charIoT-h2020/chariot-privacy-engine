#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import logging

from Crypto.PublicKey import RSA
from chariot_base.model import Alert
from chariot_base.utilities import has_write_right, has_read_right


class RsaRuleFilter(object):

    def __init__(self, engine):
        self.human_name = 'rsa_rule_filter'

        self.engine = engine
        self.actors = {
            'BMS': {
                'key': b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwusoeNOkZh8gvX7BGEy+rhRxV'
                       b'\nF/ZD11xm0UpzfTR5k/VTasjSyY1yzs2P0BePMUM78cJF21hEBL5fAFCqKpH7zhAj\nl5fFcQd'
                       b'/kZuIlB5ijJAjJhCKV8SK2rwXQXemo9Gc2PHdSg63qjYhEB55dPcClfNw\nCoWsKkKI55WtVjKsDQIDAQAB\n'
                       b'-----END PUBLIC KEY----- '
            }
        }

    def do(self, message):
        rules = self.engine.iotl.acl(message.sensor_id)
        logging.debug('Defined rules' % rules)
        if rules is not None:
            for rule in rules:
                public_key = RSA.importKey(self.actors[rule[0]]['key'])
                encrypted_msg = public_key.encrypt(message.value.encode('utf-8'), 32)[0]
                message.value = base64.b64encode(encrypted_msg).decode('utf-8')
                message.destination = rule[0]
                self.engine.publish(message)


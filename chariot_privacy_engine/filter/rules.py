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

    def do(self, message, span):
        rules = self.engine.iotl.acl(message.sensor_id)
        logging.debug('Defined rules: %s for sensor: %s' %
                      (rules, message.sensor_id))
        if rules is not None:
            for rule in rules:
                params = self.engine.iotl.params(rule[0])
                if params['type'] == 'RSA':
                    public_key = RSA.importKey(params['pubkey'])                    
                    encrypted_msg = public_key.encrypt(message.value.encode('utf-8'), 32)[0]
                    print(base64.b64encode(encrypted_msg).decode('utf-8'))
                # message.value = base64.b64encode(encrypted_msg).decode('utf-8')
                message.destination = rule[0]
                self.engine.publish(message, span)

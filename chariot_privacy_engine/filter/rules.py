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
        rules = self.engine.get_acl(span, message)
        logging.debug('Defined rules: %s for sensor: %s' %
                      (rules, message.sensor_id))
        if rules is None or len(rules) == 0:
            msg = 'Package from sensor \'{sensor_id}\' is not allowed to be delivered to anyone'.format(
                **message.dict())
            alert = Alert(self.human_name, msg, 100)
            alert.sensor_id = message.sensor_id
            self.engine.raise_alert(alert, span)
        else:
            for rule in rules:
                destination = rule[0]
                params = self.engine.get_params(span, destination)
                if params.get('type', None) == 'RSA':
                    encrypt_span = self.engine.start_span(
                        'encrypt_%s' % self.human_name, span)
                    public_key = RSA.importKey(base64.b64decode(params['pubkey']))
                    encrypted_msg = public_key.encrypt(
                        message.value.encode('utf-8'), 32)[0]
                    encoded_msg = base64.b64encode(
                        encrypted_msg).decode('utf-8')
                    self.engine.close_span(encrypt_span)
                    logging.debug('Encrypted message: %s' % encoded_msg)
                    # message.value = base64.b64encode(encrypted_msg).decode('utf-8')
                    message.destination = destination
                    self.engine.publish(message, span)
                else:
                    msg = 'Public key for \'%s\' consumer is not defined.' % destination
                    alert = Alert(self.human_name, msg, 100)
                    alert.sensor_id = message.sensor_id
                    self.engine.raise_alert(alert, span)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import logging

from Crypto.PublicKey import RSA
from chariot_base.model import Alert
from chariot_base.utilities import has_write_right, has_read_right


class RsaRuleFilter(object):

    def __init__(self, engine):
        self.human_name = 'encryption_rule_filter'
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
                key_type = params.get('pubkey_type', None)
                if key_type == 'None':
                    message = self.no_encyption(message)
                elif key_type == 'RSA':
                    message = self.rsa_encyption(span, params, message)
                elif key_type == 'ECDH':
                    message = self.ecdh_encyption(span, params, message)
                    continue
                else:
                    msg = 'Public key for \'%s\' consumer is not defined.' % destination
                    alert = Alert(self.human_name, msg, 100)
                    alert.sensor_id = message.sensor_id
                    self.engine.raise_alert(alert, span)
                    continue

                message.destination = destination
                self.engine.publish(message, span)

    def no_encyption(self, message):
        return message

    def ecdh_encyption(self, span, params, message):
        encrypt_span = self.engine.start_span(f'ecdh_encrypt_{self.human_name}', span)
        msg = 'The ECDH encyption scheme is not supported yet.'
        alert = Alert(self.human_name, msg, 100)
        alert.sensor_id = message.sensor_id
        self.engine.raise_alert(alert, span)
        self.engine.close_span(encrypt_span)
        return message

    def rsa_encyption(self, span, params, message):
        encrypt_span = self.engine.start_span(f'rsa_encrypt_{self.human_name}', span)
        public_key = RSA.importKey(base64.b64decode(params['pubkey']))
        encrypted_msg = public_key.encrypt(message.value.encode('utf-8'), 32)[0]
        encoded_msg = base64.b64encode(encrypted_msg).decode('utf-8')
        logging.debug(f'Encrypted message: {encoded_msg}')
        message.value = encoded_msg
        self.engine.close_span(encrypt_span)
        return message

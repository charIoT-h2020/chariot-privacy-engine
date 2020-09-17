#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import base64
import logging

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from chariot_base.model import Alert, Message
from chariot_base.utilities import has_write_right, has_read_right


class RsaRuleFilter(object):

    def __init__(self, engine):
        self.human_name = 'encryption_rule_filter'
        self.engine = engine

    def do(self, messages, span):
        if isinstance(messages, list):
            filtered_messages = []
            for message in messages:
                filtered_messages += self.apply_filter(message, span)
            return filtered_messages
        else:
            return self.apply_filter(message, span)

    def apply_filter(self, message, span):
        rules = self.engine.get_acl(span, message)
        logging.debug('Defined rules: %s for sensor: %s' %
                      (rules, message.sensor_id))
        if rules is None or len(rules['ALLOW']) == 0:
            msg = f'Package from sensor \'{message.sensor_id}\' is not allowed to be delivered to anyone'
            alert = Alert(self.human_name, msg, 100)
            alert.sensor_id = message.sensor_id
            self.engine.raise_alert(alert, span)
            return []
        else:
            messages = []
            for destination in rules['ALLOW']:
                params = self.engine.get_params(span, destination)
                key_type = params.get('pubkey_type', None)
                if key_type == 'None':
                    new_message = self.no_encyption(message)
                elif key_type == 'RSA':
                    new_message = self.rsa_encyption(span, params, message)
                elif key_type == 'ECDH':
                    new_message = self.ecdh_encyption(span, params, message)
                    continue
                else:
                    msg = f'Public key for \'{destination}\' consumer is not defined.'
                    alert = Alert(self.human_name, msg, 100)
                    alert.sensor_id = message.sensor_id
                    self.engine.raise_alert(alert, span)
                    continue

                new_message.destination = destination
                messages.append(new_message)

            return messages

    def no_encyption(self, message):
        new_message = Message(message.sensor_id, message.value)
        new_message.id = message.id
        return new_message

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

        data = message.value.encode('utf-8')
        base64_public_key = params['pubkey']

        serialized_public_key = base64.b64decode(base64_public_key)

        recipient_key = RSA.import_key(serialized_public_key)

        session_key = get_random_bytes(16)

        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)

        enc_session_key_d = base64.b64encode(enc_session_key).decode('utf-8')
        nonce_d = base64.b64encode(cipher_aes.nonce).decode('utf-8')
        tag_d = base64.b64encode(cipher_aes.nonce).decode('utf-8')
        ciphertext_d = base64.b64encode(ciphertext).decode('utf-8')

        encoded_msg = json.dumps([enc_session_key_d, nonce_d, tag_d, ciphertext_d])

        logging.debug(f'Encrypted message: {encoded_msg}')
        new_message = Message(message.sensor_id, encoded_msg)
        new_message.id = messages.id
        self.engine.close_span(encrypt_span)
        return new_message

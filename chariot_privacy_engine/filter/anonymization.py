#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import base64
import logging
import hashlib

from chariot_base.model import Alert

class AnonymizationFilter(object):

    def __init__(self, engine):
        self.human_name = 'anonymization_filter'
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
        details = self.engine.get_params(span, message.sensor_id)
        fields = details.get('fields', {})
        logging.debug(f'Sensor fields info: {fields}')
        try:
          payload = json.loads(message.value)
          
          for field in fields:
              field_details = fields[field]
              algo = field_details.get('anonymize', 'None')
          
              if algo == 'None':
                  continue
              elif algo == 'SHA256':
                  payload[field] = self.apply_sha256(str(payload[field]), span)
              elif algo == 'SHA512':
                  payload[field] = self.apply_sha512(str(payload[field]), span)
              elif algo == 'MD5':
                  payload[field] = self.apply_md5(str(payload[field]), span)
              else:
                  logging.debug(f'Unkwonw algorithm "{algo}"')
          message.value = json.dumps(payload)
          return [message]
        except:
          logging.debug(f'Message payload isn\'t JSON ({message.value})')
          return [message]

    def apply_sha512(self, field, span):
        m = hashlib.sha512()
        m.update(field.encode())
        return m.hexdigest()

    def apply_sha256(self, field, span):
        m = hashlib.sha256()
        m.update(field.encode())
        return m.hexdigest()

    def apply_md5(self, field, span):
        m = hashlib.md5(field.encode())
        return m.hexdigest()

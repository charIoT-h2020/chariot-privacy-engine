# -*- coding: utf-8 -*-
from Crypto.PublicKey import RSA
import base64


class RsaRuleFilter(object):

    def __init__(self):
        self.rules = {
            'bmc': {
                'permissions': {
                    'urn:ngsi-ld:temp:001': 2
                },
                'key': b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwusoeNOkZh8gvX7BGEy+rhRxV'
                       b'\nF/ZD11xm0UpzfTR5k/VTasjSyY1yzs2P0BePMUM78cJF21hEBL5fAFCqKpH7zhAj\nl5fFcQd'
                       b'/kZuIlB5ijJAjJhCKV8SK2rwXQXemo9Gc2PHdSg63qjYhEB55dPcClfNw\nCoWsKkKI55WtVjKsDQIDAQAB\n'
                       b'-----END PUBLIC KEY----- '
            }
        }

    def do(self, message):
        rule = self.rules.get(message.destination)

        if rule is not None:
            if self.has_read_right(rule.get('permissions').get(message.id, 0)):
                public_key = RSA.importKey(rule.get('key'))
                encrypted_msg = public_key.encrypt(message.value.encode('utf-8'), 32)[0]
                encoded_encrypted_msg = base64.b64encode(encrypted_msg)  # base64 encoded strings are database friendly
                print(encoded_encrypted_msg)
                return encoded_encrypted_msg
            else:
                return None
        else:
            return None

    @staticmethod
    def has_read_right(flag):
        return flag & 2 > 0

    @staticmethod
    def has_write_right(flag):
        return flag & 1 > 0

# -*- coding: utf-8 -*-
from Crypto.PublicKey import RSA
import base64

from chariot_base.model import Alert


class RsaRuleFilter(object):

    def __init__(self, engine):
        self.engine = engine
        self.actors = {
            'bms': {
                'key': b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwusoeNOkZh8gvX7BGEy+rhRxV'
                       b'\nF/ZD11xm0UpzfTR5k/VTasjSyY1yzs2P0BePMUM78cJF21hEBL5fAFCqKpH7zhAj\nl5fFcQd'
                       b'/kZuIlB5ijJAjJhCKV8SK2rwXQXemo9Gc2PHdSg63qjYhEB55dPcClfNw\nCoWsKkKI55WtVjKsDQIDAQAB\n'
                       b'-----END PUBLIC KEY----- '
            }
        }
        self.rules = {
            'temp:001': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain01': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain02': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain03': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain04': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain05': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain06': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain07': [
                ('bms', 2)
            ],
            '5410ec4d1601_ain08': [
                ('bms', 2)
            ],
            '5410ec4d1601_din01': [
                ('bms', 2)
            ],
            '5410ec4d1601_din02': [
                ('bms', 2)
            ],
            '5410ec4d1601_din03': [
                ('bms', 2)
            ],
            '5410ec4d1601_din04': [
                ('bms', 2)
            ],
            '5410ec4d1601_din05': [
                ('bms', 2)
            ],
            '5410ec4d1601_din06': [
                ('bms', 2)
            ],
            '5410ec4d1601_din07': [
                ('bms', 2)
            ],
            '5410ec4d1601_din08': [
                ('bms', 2)
            ],
            '5410ec4d1601_din09': [
                ('bms', 2)
            ],
            '5410ec4d1601_din10': [
                ('bms', 2)
            ],
            '5410ec4d1601_din11': [
                ('bms', 2)
            ],
            '5410ec4d1601_din12': [
                ('bms', 2)
            ],
            '5410ec4d1601_din13': [
                ('bms', 2)
            ],
            '5410ec4d1601_din14': [
                ('bms', 2)
            ],
            '5410ec4d1601_din15': [
                ('bms', 2)
            ],
            '5410ec4d1601_din16': [
                ('bms', 2)
            ],
            '5410ec4d1601_humidity': [
                ('bms', 2)
            ],
            '5410ec4d1601_temperature': [
                ('bms', 2)
            ],
            '5410ec4d1601_battery_voltage': [
                ('bms', 2)
            ]
        }

    def do(self, message):
        rules = self.rules.get(message.sensor_id)

        if rules is not None:
            for rule in rules:
                public_key = RSA.importKey(self.actors[rule[0]]['key'])
                encrypted_msg = public_key.encrypt(message.value.encode('utf-8'), 32)[0]
                message.value = base64.b64encode(encrypted_msg).decode('utf-8')
                message.destination = rule[0]
                self.engine.publish(message)

    @staticmethod
    def has_read_right(flag):
        return flag & 2 > 0

    @staticmethod
    def has_write_right(flag):
        return flag & 1 > 0

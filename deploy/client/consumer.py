# -*- coding: utf-8 -*-
import base64
from Crypto import Random
from Crypto.PublicKey import RSA
import paho.mqtt.client as mqtt


mqtt.Client.connected_flag = False
key = ''

def decrypt_message(encoded_encrypted_msg, private_key):
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decoded_decrypted_msg = private_key.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_msg


def on_message(client, userdata, message):
    print("message received  ", str(message.payload.decode("utf-8")), "topic", message.topic, "retained ", message.retain)
    if message.retain == 1:
        print("This is a retained message")


def on_log(client, userdata, level, buf):
    print("log: ", buf)


# Initialize connection to northbound
broker = '172.18.1.3'
consumer = mqtt.Client('consumer')
consumer.connect(broker)

consumer.on_log = on_log
consumer.on_message = on_message

consumer.subscribe([
    ('bms/#', 0),
    ('dashboard/alerts', 1)
])

consumer.loop_forever()

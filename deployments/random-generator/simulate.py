# -*- coding: utf-8 -*-

import os
import uuid
import datetime
import json
import gmqtt
import asyncio
import signal
import logging
import random
import time

from chariot_base.utilities import open_config_file
from chariot_base.connector import LocalConnector, create_client


class RndTrafficConnector(LocalConnector):
    def __init__(self):
        super(RndTrafficConnector, self).__init__()
        self.engine = None


STOP = asyncio.Event()


def ask_exit(*args):
    logging.info('Stoping....')
    STOP.set()

def generate_gateway_message(rndTraffic, gw):
    mac = gw["mac"]
    logging.debug(f'Send message from {mac}')

    inputs = {}
    for i in range(0, gw['analog']):
        id = '{:0>2}'.format(i)
        inputs[f'ain{id}'] = random.randint(1000, 2000)

    for i in range(0, gw['digital']):
        id = '{:0>2}'.format(i)
        inputs[f'din{id}'] = random.randint(0, 1)

    msg = {
        "package_id": str(uuid.uuid4()),
        "sensor_id": mac,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "value": inputs
    }

    logging.debug(f'Message: {json.dumps(msg)}')
    rndTraffic.publish('privacy', msg)

def generate_sensor_message(rndTraffic, sensor):
    connectiontType = sensor.get('type', 'wifi')

    logging.debug(f'Send message {sensor["mac"]}-{sensor.get("authenticated", True)}')

    sensorValues = { }
    if sensor.get('authenticated', True) == False:
        status_code = 2
        status_message = 'Sensor without authentication'
    else:
        status_code = 0
        status_message = 'Sensor online'

        for attr in sensor.get('values', []):
            type = attr.get('type', 'numeric')
            if type == 'numeric':
                rval = random.uniform(attr['min'], attr['max'])
                sensorValues[attr['name']] = str(rval)
            elif type == 'boolean':
                rval = random.randint(0, 1)
                sensorValues[attr['name']] = str(rval)
            elif type == 'identity':
                rval = f'{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}'
                sensorValues[attr['name']] = str(rval)
            else:
                logging.error(f'Not supported type {type}')

    msg = {
        "package_id": str(uuid.uuid4()),
        "sensor_id": sensor["mac"],
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "value": sensorValues
    }

    logging.debug(f'Message: {json.dumps(msg)}')    
    rndTraffic.publish('privacy', msg)


async def main(args=None):
    opts = open_config_file()

    sensors = opts.simulation['sensors']
    gateways = opts.simulation['gateways']
    interval = opts.simulation['interval']

    client = await create_client(opts.brokers.southbound, 'demo_client')

    rndTraffic = RndTrafficConnector()
    rndTraffic.register_for_client(client)

    while not STOP.is_set():
        logging.info('Send messages')

        for sensor in sensors:
            generate_sensor_message(rndTraffic, sensor)

        for gateway in gateways:
            generate_gateway_message(rndTraffic, gateway)

        logging.info(f'Wait {interval}sec')
        await asyncio.sleep(interval)
    
    await STOP.wait()
    await client.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
    logging.info('Stopped....')

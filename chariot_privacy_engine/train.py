# -*- coding: utf-8 -*-

import os
import uuid
import json
import logging
import pandas as pd

from chariot_privacy_engine.helpers.DataFrameClient import DataFrameClient

from chariot_base.utilities import open_config_file

class TrainService:

    def __init__(self, options={}):
        self.options = options
        self.db = self.init_db(**options['cognitive']['database'])


    def init_db(self, host, port, username, password, database, path, duration='4w'):
        logging.debug(f'{host}/{path}:{port} <{username}> ({database})')
        db = DataFrameClient(host=host, port=port, username=username, password=password, database=database, path=path)
        return db

    def query_raw_data(self):
        results  = self.db.query(f'SELECT "is_sensitive", "sensor_id", "value", "value_name" FROM "awesome_policy"."instances"', 
                                 database=self.options['cognitive']['database']['database'])
        points = results 
        logging.debug(points)
        # for point in points:
        #     logging.debug(f'{point["time"]}, {point["sensor_id"]}, {point["value"]}, {point["value_name"]}, {point["is_sensitive"]}')

def main(args=None):
    opts = open_config_file()
    options_engine = opts.privacy_engine
    service = TrainService(options_engine)
    service.query_raw_data()

if __name__ == '__main__':
    main()
    logging.info('Stopped....')

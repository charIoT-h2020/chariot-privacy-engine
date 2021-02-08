# -*- coding: utf-8 -*-

import os
import uuid
import json
import logging
import numpy
import pandas as pd

from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from chariot_privacy_engine.helpers.DataFrameClient import DataFrameClient

from chariot_base.utilities import open_config_file
from chariot_privacy_engine.training import TrainService

def main(args=None):
    opts = open_config_file()
    options_engine = opts.privacy_engine
    service = TrainService(options_engine)
    dataset = service.query_data()
    dataset.to_csv('test.csv')
    service.train(dataset)

if __name__ == '__main__':
    main()
    logging.info('Stopped....')

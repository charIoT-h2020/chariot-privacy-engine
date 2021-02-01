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

# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)

def create_baseline():
	model = Sequential()
	model.add(Dense(65, input_dim=65, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
    
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

# smaller model
def create_smaller():
	# create model
	model = Sequential()
	model.add(Dense(65, input_dim=65, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
	# Compile model
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

def create_larger():
	# create model
	model = Sequential()
	model.add(Dense(60, input_dim=60, kernel_initializer='normal', activation='relu'))
	model.add(Dense(30, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
	# Compile model
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

class TrainService:

    def __init__(self, options={}):
        self.options = options
        self.db = self.init_db(**options['cognitive']['database'])


    def init_db(self, host, port, username, password, database, path, duration='4w'):
        logging.debug(f'{host}/{path}:{port} <{username}> ({database})')
        db = DataFrameClient(host=host, port=port, username=username, password=password, database=database, path=path)
        return db

    def transform(self, row):
        sensor_id = row['sensor_id']
        value_name = row['value_name']
        is_sensitive = row['is_sensitive']        
        value = row['value']

        d = [0]*64
        for char in value.upper():
            index = ord(char) - 32
            if index < 0 or index > 64:
                pass
            else:
                d[index] = d[index] + 1

        is_number = 1
        try:
            value = float(value)
        except:
            is_number = 0

        is_fw_event = 1
        if value_name == 'ftpFwUpdEventText' or value_name == 'ftpFwUpdErrorCode' or value_name == 'ftpFwUpdEventCode':
            is_fw_event = 0

        new_row = [sensor_id, value_name, value, is_fw_event, is_number] + d

        if is_sensitive:
            new_row.append(1)
        else:
            new_row.append(0)
        return new_row

    def query_data(self):
        results = self.db.query(f'SELECT "sensor_id", "value_name", "value", "is_sensitive" FROM "awesome_policy"."instances"', 
                                 database=self.options['cognitive']['database']['database'])
        df = results['instances']
        new_data = []
        for index, row in df.iterrows():
            new_data.append(self.transform(row))

        cols = ['sensor_id', 'value_name', 'value', 'is_fw_event', 'is_number']
        for i in range(0, 64):
            cols.append(chr(i+32))
        cols.append('is_sensitive')

        return pd.DataFrame(new_data, columns=cols)

    def train(self, dataframe):
        dataset = dataframe.values

        # # split into input (X) and output (Y) variables
        X = dataset[:,3:68].astype(float)
        Y = dataset[:,69]
        # pass
        encoder = LabelEncoder()
        encoder.fit(Y)
        encoded_Y = encoder.transform(Y)

        estimator = KerasClassifier(build_fn=create_baseline, epochs=100, batch_size=5, verbose=0)
        kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
        results = cross_val_score(estimator, X, encoded_Y, cv=kfold)
        print("Results: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

        # evaluate baseline model with standardized dataset
        numpy.random.seed(seed)
        estimators = []
        estimators.append(('standardize', StandardScaler()))
        estimators.append(('mlp', KerasClassifier(build_fn=create_baseline, epochs=100, batch_size=5, verbose=0)))
        pipeline = Pipeline(estimators)
        kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
        results = cross_val_score(pipeline, X, encoded_Y, cv=kfold)
        print("Standardized: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

        estimators = []
        estimators.append(('standardize', StandardScaler()))
        estimators.append(('mlp', KerasClassifier(build_fn=create_smaller, epochs=100, batch_size=5, verbose=0)))
        pipeline = Pipeline(estimators)
        kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
        results = cross_val_score(pipeline, X, encoded_Y, cv=kfold)
        print("Smaller: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

        estimators = []
        estimators.append(('standardize', StandardScaler()))
        estimators.append(('mlp', KerasClassifier(build_fn=create_larger, epochs=100, batch_size=5, verbose=0)))
        pipeline = Pipeline(estimators)
        kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
        results = cross_val_score(pipeline, X, encoded_Y, cv=kfold)
        print("Larger: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))


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

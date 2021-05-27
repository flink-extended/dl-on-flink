import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from code import census_dataset


def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def preprocess(input_dict):
    feature_dict = {
        'age': _float_feature(value=int(input_dict['age'])),
        'workclass': _bytes_feature(value=input_dict['workclass'].encode()),
        'fnlwgt': _float_feature(value=int(input_dict['fnlwgt'])),
        'education': _bytes_feature(value=input_dict['education'].encode()),
        'education_num': _float_feature(value=int(input_dict['education_num'])),
        'marital_status': _bytes_feature(value=input_dict['marital_status'].encode()),
        'occupation': _bytes_feature(value=input_dict['occupation'].encode()),
        'relationship': _bytes_feature(value=input_dict['relationship'].encode()),
        'race': _bytes_feature(value=input_dict['race'].encode()),
        'gender': _bytes_feature(value=input_dict['gender'].encode()),
        'capital_gain': _float_feature(value=int(input_dict['capital_gain'])),
        'capital_loss': _float_feature(value=int(input_dict['capital_loss'])),
        'hours_per_week': _float_feature(value=float(input_dict['hours_per_week'])),
        'native_country': _bytes_feature(value=input_dict['native_country'].encode()),
    }
    model_input = tf.train.Example(features=tf.train.Features(feature=feature_dict))
    model_input = model_input.SerializeToString()
    return model_input


def get_accuracy_score(model_path, data_path, max_sample_num=None):
    predictor = tf.contrib.predictor.from_saved_model(model_path)
    data = pd.read_csv(data_path, names=census_dataset.CSV_COLUMNS)
    label = data.pop('income_bracket')
    label = label.map({'<=50K': 0, '>50K': 1})
    inputs = []
    data = data[:max_sample_num]
    label = label[:max_sample_num]
    for _, row in data.iterrows():
        tmp = dict(zip(census_dataset.CSV_COLUMNS[:-1], row))
        tmp = preprocess(tmp)
        inputs.append(tmp)
    output_dict = predictor({'inputs': inputs})
    res = [np.argmax(output_dict['scores'][i]) for i in range(0, len(output_dict['scores']))]
    return accuracy_score(label, res)

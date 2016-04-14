#!/usr/bin/python

import os
import json
import re 
import numpy as np
from sklearn.utils import check_random_state
pattern = re.compile('[\W_]+')

class Bunch(dict):
    """Container object for datasets
    Dictionary-like object that exposes its keys as attributes.
    >>> b = Bunch(a=1, b=2)
    >>> b['b']
    2
    >>> b.b
    2
    >>> b.a = 3
    >>> b['a']
    3
    >>> b.c = 6
    >>> b['c']
    6
    """

    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass

def preprocess_text(text):
    #- lowercase
    #- strip everything but numbers and chars

    #- lowercase
    clean_text = text.lower()
    #- strip everything but numbers and chars
    clean_text = pattern.sub('', clean_text)

    return clean_text

def fetch_data(indir, y_value=1):
    # return data with appropriate label
    # read and preprocess text, then assign label
    data = []
    target = []
    for fname in os.listdir(indir):
        for line in open(indir+'/'+fname):
            data.append(preprocess_text(json.loads(line)['extract_text']))
            target.append(y_value)
    return Bunch(data=data, target=np.array(target))

def split_train_test(positive_data, negative_data, ratio=0.5):
    # return train and test data

    #merge
    data = positive_data.data + negative_data.data
    target = np.concatenate((positive_data.target, negative_data.target))
    all_data = Bunch(data=data, target=target)
    
    #shuffle
    random_state = check_random_state(42)
    indices = np.arange(all_data.target.shape[0])
    random_state.shuffle(indices)
    all_data.target = all_data.target[indices]
    # Use an object array to shuffle: avoids memory copy
    data_lst = np.array(all_data.data, dtype=object)
    data_lst = data_lst[indices]
    all_data.data = data_lst.tolist()

    split_point = int(all_data.target.shape[0] * ratio)
    data_train = Bunch(data = all_data.data[:split_point], target = all_data.target[:split_point])
    data_test = Bunch(data = all_data.data[split_point:], target = all_data.target[split_point:])
    return data_train, data_test

def prepare_data(positive_dir, negative_dir):
    positive_data = fetch_data(positive_dir, 1)
    negative_data = fetch_data(negative_dir, 0)
    data_train, data_test = split_train_test(positive_data, negative_data, 0.5)
    return data_train, data_test

def test_preprocess():
    print preprocess_text("aDKJJGEflkk323*6ld^^^j")

def test():
    prepare_data("pos", "neg")

test()
    

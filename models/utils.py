#!/usr/bin/python

import os
import json
import re 
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.utils import check_random_state
# from sklearn.preprocessing import MultiLabelBinarizer
pattern = re.compile('[\W_]+')
import traceback

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
    clean_text = pattern.sub(' ', clean_text)

    return clean_text

def get_property_text(prop):
    prop_text = ''
    for prop_child in prop['properties'].values():
        if len(prop_child) == 0: continue
        for prop_child_child in prop_child:
            # print "xxx", prop_child_child
            if type(prop_child_child) == type({}):
                prop_text += ' ' + get_property_text(prop_child_child)
            else:
                prop_text += ' ' + prop_child_child
    return prop_text

def extract_features(indir):
    #Extract features from schema.org values
    #Return a list of features
    features = set([]) 
    if os.path.isdir(indir):
        for fname in os.listdir(indir):
            if fname.split(".")[-1] != "json":
                print "Wrong file: " + fname
                continue
            print "Processing " + fname
            for line in open(indir+'/'+fname):
                if (max != -1) & (count > max) :
                    return Bunch(data=data, target=np.array(target))
                count +=1 
                try:
                    if count %10000 == 0:
                        print " Processed " + str(count) + " records"
                    jsonobj = json.loads(line)
                    microdata_list = jsonobj['microdata']
                    property_text = ""
                    for microdata in microdata_list: 
                        property_text += " " + preprocess_text(get_property_text(microdata))
                    tokens = property_text.split()
                    for token in tokens:
                        features.add(token)
                except:
                    traceback.print_exc()
    return features

def fetch_data(indir, label=1, max = -1):
    # read and preprocess text, then assign label. 
    # max: maximum number of records to be loaded. if max == -1, load everything
    # label: 1 if indir contains positive data, 0 if negative data
    data = []
    target = []
    count = 0
    if os.path.isdir(indir):
        for fname in os.listdir(indir):
            if fname.split(".")[-1] != "json":
                print "Wrong file: " + fname
                continue
            print "Processing " + fname
            for line in open(indir+'/'+fname):
                if (max != -1) & (count > max) :
                    return Bunch(data=data, target=np.array(target))
                count +=1 
                try:
                    if count %10000 == 0:
                        print " Processed " + str(count) + " records"
                    jsonobj = json.loads(line)
                    data.append(preprocess_text(jsonobj['text']))
                    target.append(label)
                except:
                    traceback.print_exc()
    return Bunch(data=data, target=np.array(target))

def fetch_data_byfile(infile, label=1, max = -1):
    # read and preprocess text, then assign label. 
    # max: maximum number of records to be loaded. if max == -1, load everything
    # label: 1 if indir contains positive data, 0 if negative data
    data = []
    target = []
    count = 0
    with open(infile) as lines:
        for line in lines:
            count += 1
            try:
                if count %10000 == 0:
                    print " Processed " + str(count) + " records"
                jsonobj = json.loads(line)
                data.append(preprocess_text(jsonobj['text']))
                target.append(label)
            except:
                traceback.print_exc()

    if (max != -1) & (len(target) > max):
        #shuffle        
        print "Shuffle negative examples"
        random_state = check_random_state(100)
        indices = np.arange(len(target))
        random_state.shuffle(indices)

        data_lst = np.array(data, dtype=object)

        data_lst = data_lst[indices]
        data = data_lst.tolist()
        data = data[:max]
        target = target[:max]

    return Bunch(data=data, target=np.array(target))


def split_train_test(positive_data, negative_data, ratio=0.5):
    # return train and test data

    #merge
    data = positive_data.data + negative_data.data
    target = np.concatenate((positive_data.target, negative_data.target))
    all_data = Bunch(data=data, target=target)
    print len(all_data.data)
    
    #shuffle
    random_state = check_random_state(100)
    indices = np.arange(all_data.target.shape[0])
    random_state.shuffle(indices)
    all_data.target = all_data.target[indices]
    # Use an object array to shuffle: avoids memory copy
    data_lst = np.array(all_data.data, dtype=object)
    data_lst = data_lst[indices]
    all_data.data = data_lst.tolist()

    split_point = int(all_data.target.shape[0] * ratio)
    positive_size = split_point
    
    data_train = Bunch(data = all_data.data[:positive_size], target = all_data.target[:positive_size])
    data_test = Bunch(data = all_data.data[split_point:], target = all_data.target[split_point:])

    print "Total number of data points: " + str(len(all_data.data))
    print "Number of data points in training data: " + str(len(data_train.data))
    print "Number of data points in test data: " + str(len(data_test.data))
    return data_train, data_test

def prepare_data_bydir(positive_dir, negative_dir, neg_2_pos_ratio = 1, train_2_all_ratio=0.5):
    positive_data = fetch_data(positive_dir, 1)
    positive_size = len(positive_data.data)
    negative_data = fetch_data(negative_dir, 0, positive_size*neg_2_pos_ratio)
    data_train, data_test = split_train_test(positive_data, negative_data, train_2_all_ratio)
    return data_train, data_test

def prepare_data_byfile(positive_file, negative_file, neg_2_pos_ratio = 1, train_2_all_ratio=0.5):
    positive_data = fetch_data_byfile(positive_file, 1)
    positive_size = len(positive_data.data)
    print "Size of positive examples: " + str(len(positive_data.data))
    negative_data = fetch_data_byfile(negative_file, 0, positive_size*neg_2_pos_ratio)
    print "Size of negative examples: " + str(len(negative_data.data))
    data_train, data_test = split_train_test(positive_data, negative_data, train_2_all_ratio)
    return data_train, data_test

def prepare_data_byvector(pos_list, neg_list, neg_2_pos_ratio = 1, train_2_all_ratio=0.5):
    print "Shuffle negative examples" 
    print "neg_list before shuffling"
    print neg_list[0]
    random_state = check_random_state(100)
    indices = np.arange(len(neg_list))
    random_state.shuffle(indices)
    print len(indices)
    print indices[:10]
    neg_np = np.array(neg_list, dtype=object)
    neg_np = neg_np[indices]
        
    max = len(pos_list)*neg_2_pos_ratio
    neg_list = neg_np.tolist()
    neg_list = neg_list[:max]
    neg_target = [0]*len(neg_list)
    print "neg_list"
    print neg_list[0]
    negative_data = Bunch(data=neg_list, target=np.array(neg_target))
    print "Number of negative examples: " + str(len(neg_list))

    pos_target = [1]*len(pos_list)
    positive_data = Bunch(data=pos_list, target=np.array(pos_target))
    print "Number of positive examples: " + str(len(pos_list))

    data_train, data_test = split_train_test(positive_data, negative_data, train_2_all_ratio)
    return data_train, data_test

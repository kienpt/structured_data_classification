import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.utils import check_random_state
import pickle
import json
from time import time
import traceback
import numpy as np

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

def load_data(infile, ratio=0.8):
    '''
    1. Read json data
    2. Shuffle
    3. Split train and test
    4. Return train and test for both fulltext and structured data
    '''
    full_data = []
    structured_data = []
    full_target = []
    target_names = set([])
    count = 0
    print "Loading"
    for line in open(infile):
        try:
            count += 1
            if count%1000==0:
                print count
            obj= json.loads(line)
            target_names.add(obj['one_topic'])
            full_data.append(obj['fulltext'])
            full_target.append(obj['one_topic'])

            structured_data.append(obj['structured_data'])
        except:
            traceback.print_exc()
    #full_data = np.array(full_data)
    #structured_data = np.array(structured_data)
    full_target = np.array(full_target)

    print"Shuffling"
    #shuffle
    random_state = check_random_state(42)
    indices = np.arange(full_target.shape[0])
    random_state.shuffle(indices)
    full_target = full_target[indices]

    # Use an object array to shuffle: avoids memory copy
    data_lst = np.array(full_data, dtype=object)
    data_lst = data_lst[indices]
    full_data = data_lst.tolist()
    
    data_lst = np.array(structured_data, dtype=object)
    data_lst = data_lst[indices]
    structured_data = data_lst.tolist()

    print"Splitting"
    #split
    split_point = int(len(full_target) * ratio)
    structured_data_train = []
    structured_target_train = []
    structured_data_test = []
    structured_target_test = []
    for i in range(split_point):
        for sd in structured_data[i]:
            structured_data_train.append(sd)
            structured_target_train.append(full_target[i])
    for i in range(split_point, len(full_target)):
        for sd in structured_data[i]:
            structured_data_test.append(sd)
            structured_target_test.append(full_target[i])

    train = Bunch(gData=full_data[:split_point], gTarget=np.array(full_target[:split_point]), lData=structured_data_train, lTarget=structured_target_train, target_names=list(target_names))
    test = Bunch(gData=full_data[split_point:], gTarget=np.array(full_target[split_point:]), lData=structured_data_test, lTarget=structured_target_test, target_names=list(target_names))
    
    return train, test

class JointModel():
    
    def __init__(self):
        self.gModel = LinearSVC(loss='l2', penalty='l2', dual=False, tol=1e-3)#global model that trained by fulltext
        self.lModel = LinearSVC(loss='l2', penalty='l2', dual=False, tol=1e-3)#local model that trained by structured data
        self.gVectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                 stop_words='english')
        self.lVectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                 stop_words='english')

    def fit(self, data_train):
        gx = self.gVectorizer.fit_transform(data_train.gData)
        lx = self.lVectorizer.fit_transform(data_train.lData)
       
        t0 = time()
        self.gModel.fit(gx, data_train.gTarget)
        train_time = time() - t0
        print("train time of global model: %0.3fs" % train_time)
        pickle.dump(self.gModel, open('gmodel.skl', 'w'))

        t0 = time()
        self.lModel.fit(lx, data_train.lTarget)
        train_time = time() - t0
        print("train time of local model: %0.3fs" % train_time)
        pickle.dump(self.lModel, open('lmodel.skl', 'w'))

    def split(self, text, size=100, step=50):
        #Slide text into overlapped windows
        words = text.split()
        windows = []
        for i in range(0, len(words)-size, step):
            wd = ' '.join(words[i:i+size])
            windows.append(wd)
        #print "Text1: " +  windows[0]
        #print "Text2: " + windows[1]
        #print "Text3: " + windows[2]
        return windows

    def test(self, data_test):
        gx = data_test.gData
        gy = data_test.gTarget
        count = 0
        for i in range(len(gx)):
            fulltext = gx[i]
            predict_label = self.predict(fulltext)
            if predict_label == gy[i]:
                count += 1
        #print "Accuracy = " + str(float(count)/len(gx))

    def predict(self, sample):
        windowns = self.split(sample)
        vecWindowns = self.lVectorizer.transform(windowns)
        lScore = self.lModel.decision_function(vecWindowns)
        print "lScore"
        print lScore.shape
        vecSample = self.gVectorizer.transform(sample)
        gScore = self.gModel.decision_function(vecSample)
        print "gScore"
        print gScore.shape
        return None        

def main():
    infile = sys.argv[1]
    train, test = load_data(infile)
    print "Done loading data"

    jm = JointModel()
    jm.fit(train)
    jm.test(test)



if __name__=="__main__":
    main()

from __future__ import print_function

import logging
import numpy as np
import os
from optparse import OptionParser
import sys
from time import time
import matplotlib.pyplot as plt
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.extmath import density
from sklearn import metrics
import utils
import pickle


# Benchmark classifiers
def benchmark(clf, X_train, y_train, X_test, y_test, opts):
    print('_' * 80)
    print("Training: ")
    print(clf)
    t0 = time()
    clf.fit(X_train, y_train)
    train_time = time() - t0
    print("train time: %0.3fs" % train_time)

    t0 = time()
    pred = clf.predict(X_test)
    test_time = time() - t0
    print("test time:  %0.3fs" % test_time)

    recall = metrics.recall_score(y_test, pred)
    print("recall:   %0.3f" % recall)
    precision = metrics.precision_score(y_test, pred)
    print("precision:   %0.3f" % precision)
    f1score = metrics.f1_score(y_test, pred)
    print("f1 score:   %0.3f" % f1score)

    if hasattr(clf, 'coef_'):
        print("dimensionality: %d" % clf.coef_.shape[1])
        print("density: %f" % density(clf.coef_))

        if opts.print_top10 and feature_names is not None:
            print("top 10 keywords per class:")
            for i, category in enumerate(categories):
                top10 = np.argsort(clf.coef_[i])[-10:]
                print(trim("%s: %s"
                      % (category, " ".join(feature_names[top10]))))
        print()

    if opts.print_report:
        print("classification report:")
        print(metrics.classification_report(y_test, pred,
                                            target_names=categories))

    if opts.print_cm:
        print("confusion matrix:")
        print(metrics.confusion_matrix(y_test, pred))

    print()
    clf_descr = str(clf).split('(')[0]
    return clf_descr, f1score, train_time, test_time

def trim(s):
    """Trim string to fit on terminal (assuming 80-column display)"""
    return s if len(s) <= 80 else s[:77] + "..."


def get_parameters():
    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    
    
    # parse commandline arguments
    op = OptionParser()
    op.add_option("--action",
                  action="store", type="string", dest="action",
                  help="train,predict")
    #Train
    op.add_option("--report",
                  action="store_true", dest="print_report",
                  help="Print a detailed classification report.")
    op.add_option("--pos_file",
                  action="store", type="string", dest="positive_file",
                  help="file with positive examples")
    op.add_option("--neg_file",
                  action="store", type="string", dest="negative_file",
                  help="file with negative examples")
    op.add_option("--confusion_matrix",
                  action="store_true", dest="print_cm",
                  help="Print the confusion matrix.")
    op.add_option("--model_file",
                  action="store", type="string", dest="model_file",
                  help="file to save the model")
    op.add_option("--vect_file",
                  action="store", type="string", dest="vect_file",
                  help="file to save the vectorizer")
    #Classify
    op.add_option("--index_file",
                  action="store", type="string", dest="index_file",
                  help="file with all sentences and indices of positive and negative sentences for each property")
    op.add_option("--prop_names_file",
                  action="store", type="string", dest="prop_names_file",
                  help="file contains property names")
    op.add_option("--model_dir",
                  action="store", type="string", dest="model_dir",
                  help="directory contains both model and vectorizer files")
    op.add_option("--classify_outfile",
                  action="store", type="string", dest="classify_outfile",
                  help="output file that contains classification scores of all sentences")
    #boost
    #--classify_outfile
    op.add_option("--windown_size",
                  action="store", type="int", dest="windown_size",
                  help="size of the windown surrounding predicting sentence")

    op.add_option("--prop_name",
                  action="store", type="string", dest="prop_name",
                  help="name of the property to be considering")

    #others
    op.add_option("--chi2_select",
                  action="store", type="int", dest="select_chi2",
                  help="Select some number of features using a chi-squared test")
    op.add_option("--top10",
                  action="store_true", dest="print_top10",
                  help="Print ten most discriminative terms per class"
                       " for every classifier.")
    op.add_option("--use_hashing",
                  action="store_true",
                  help="Use a hashing vectorizer.")
    op.add_option("--n_features",
                  action="store", type=int, default=2 ** 16,
                  help="n_features when using the hashing vectorizer.")
    
    (opts, args) = op.parse_args()
    if len(args) > 0:
        op.error("this script takes no arguments.")
        sys.exit(1)
    
    print(__doc__)
    op.print_help()
    print()
    return opts

def train(opts):
    print("Loading data...")
    neg2pos_ratio = 1 #neg examples are twice pos ones
    train2all_ratio= 0.5 #20
    data_train, data_test = utils.prepare_data_byfile(opts.positive_file, opts.negative_file, neg2pos_ratio, train2all_ratio)
    
    categories = ['negative', 'positive']
     
    def size_mb(docs):
        return sum(len(s.encode('utf-8')) for s in docs) / 1e6
    data_train_size_mb = size_mb(data_train.data)
    data_test_size_mb = size_mb(data_test.data)
    print("%d documents - %0.3fMB (training set)" % (
        len(data_train.data), data_train_size_mb))
    print("%d documents - %0.3fMB (test set)" % (
        len(data_test.data), data_test_size_mb))
    print("%d categories" % len(categories))
    print()
    
    # split a training set and a test set
    y_train, y_test = data_train.target, data_test.target
    
    if opts.use_hashing:
        vectorizer = HashingVectorizer(stop_words='english', non_negative=True,
                                       n_features=opts.n_features)
        X_train = vectorizer.transform(data_train.data)
    else:
        vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                     stop_words='english')
        X_train = vectorizer.fit_transform(data_train.data)
    print("n_samples: %d, n_features: %d" % X_train.shape)
    print("Extracting features from the test data using the same vectorizer")
    X_test = vectorizer.transform(data_test.data)
    print("n_samples: %d, n_features: %d \n" % X_test.shape)

    '''
    #Print training data for test purpose
    trainf = open("train_test.txt", "w")
    for item in data_train.data:
        trainf.write(item + "\n")
    trainf.close()


    #end test
    '''

    # mapping from integer feature name to original token string
    if opts.use_hashing:
        feature_names = None
    else:
        feature_names = vectorizer.get_feature_names()
    
    if opts.select_chi2:
        print("Extracting %d best features by a chi-squared test" %
              opts.select_chi2)
        t0 = time()
        ch2 = SelectKBest(chi2, k=opts.select_chi2)
        X_train = ch2.fit_transform(X_train, y_train)
        X_test = ch2.transform(X_test)
        if feature_names:
            # keep selected feature names
            feature_names = [feature_names[i] for i
                             in ch2.get_support(indices=True)]
        print("done in %fs" % (time() - t0))
        print()
    
    if feature_names:
        feature_names = np.asarray(feature_names)

    clf = LinearSVC(loss='l2', penalty='l2', dual=False, tol=1e-3) 
    benchmark(clf, X_train, y_train, X_test, y_test, opts)

    #Saving the model and vectorizer 
    if opts.model_file:
        with open(opts.model_file, "wb") as f:
            pickle.dump(clf, f)
    if opts.vect_file:
        with open(opts.vect_file, "wb") as f:
            pickle.dump(vectorizer, f)

def read_prop_names(prop_names_file):
    names = []
    with open(prop_names_file) as lines:
        for line in lines:
            names.append(line.strip())
    return names

def classify(opts): 
    prop_names = read_prop_names(opts.prop_names_file)
    models = []
    vects = [] #vectorizers
    for name in prop_names:
        model_file = opts.model_dir + "/" + name + ".model"
        vect_file = opts.model_dir + "/" + name + ".vect"
        if os.path.exists(model_file):
            print("Loading " + model_file)
            model = pickle.load(open(model_file, "rb"))
            print("Loading " + vect_file)
            vect = pickle.load(open(vect_file, "rb"))
            models.append(model)
            vects.append(vect)
    print("Classifying")
    out = open(opts.classify_outfile, "w")
    with open(opts.index_file) as lines:
        for line in lines:
            obj = json.loads(line)
            processed_sentences = [utils.preprocess_text(i) for i in obj['text']] 
            obj['scores'] = []
            for i in range(len(models)):
                X = vects[i].transform(processed_sentences) 
                scores = models[i].decision_function(X)
                obj['scores'].append(scores.tolist())
            out.write(json.dumps(obj) + "\n")
    out.close()

def boost(opts):
    '''
    Flatten all scores in the windown 
    '''
    '''
    name = "title"
    name = "description"
    name = "ingredients"
    name = "recipeInstructions"
    '''
    name = opts.prop_name
    print(name)
    set_pos = set([])
    set_neg = set([])
    pos = []
    neg = []
    with open(opts.classify_outfile) as lines:
        for line in lines:
            obj = json.loads(line)
            if ("recipeInstructions" in obj['microdata']) | ("ingredients" in obj['microdata']):
                if name in obj['microdata']:
                    pos_indices = obj['microdata'][name]
                    for idx in pos_indices:
                        text = obj['text'][idx]
                        if text not in set_pos:
                            vec = []
                            set_pos.add(text)
                            for i in range(idx-opts.windown_size, idx+opts.windown_size+1):
                                if (i < 0)|(i>=len(obj['scores'][0])):
                                    vec = vec + [-1] * len(obj['scores'])
                                else:
                                    for scores in obj['scores']:
                                        vec.append(scores[i])
                            pos.append(vec)
                if name in obj['negative']: #all objects should have negative, why some don't???
                    neg_indices = obj['negative'][name]
                    for idx in neg_indices:
                        text = obj['text'][idx]
                        if text not in set_neg:
                            vec = []
                            set_neg.add(text)
                            for i in range(idx-opts.windown_size, idx+opts.windown_size+1):
                                if (i < 0)|(i>=len(obj['scores'][0])):
                                    vec = vec + [-1] * len(obj['scores'])
                                else:
                                    for scores in obj['scores']:
                                        vec.append(scores[i])
                            neg.append(vec)
    print(len(neg))

    neg2pos_ratio = 1 #neg examples are twice pos ones
    train2all_ratio= 0.5 #20

    data_train, data_test  = utils.prepare_data_byvector(pos, neg, neg2pos_ratio, train2all_ratio)
    X_train = data_train.data
    X_test = data_test.data
    y_train, y_test = data_train.target, data_test.target
    for a in range(10):
        print(X_train[20000+a][0])
        print(y_train[20000+a])
        print(X_test[20000+a][0])
        print(y_test[20000+a])

    clf = LinearSVC(loss='l2', penalty='l2', dual=False, tol=1e-3) 
    benchmark(clf, X_train, y_train, X_test, y_test, opts)

def boost_avg(opts):
    '''
    Get the avg and the std of the scores in the windown
    '''
    name = opts.prop_name
    print(name)
    set_pos = set([])
    set_neg = set([])
    pos = []
    neg = []

    with open(opts.classify_outfile) as lines:
        for line in lines:
            obj = json.loads(line)
            if ("recipeInstructions" in obj['microdata']) | ("ingredients" in obj['microdata']):
            #Only consider pages that have instruction and ingredient
                if name in obj['microdata']:
                    pos_indices = obj['microdata'][name]
                    for idx in pos_indices:
                    #for each positive example
                        text = obj['text'][idx]
                        if text not in set_pos:
                        #make sure that a positive example is not considered twice.  
                            #compute the avg and std of the surrounding
                            vec = []
                            set_pos.add(text)
                            temps = [] #Use to store intermediate scores for computing avg and std
                            for j in range(len(obj['scores'])):
                                temps.append([])
                            for i in range(idx-opts.windown_size, idx+opts.windown_size+1):
                                if i == idx:
                                    continue
                                if (i < 0)|(i>=len(obj['scores'][0])):
                                    for temp in temps:
                                        temp.append(-1)
                                else:
                                    for j in range(len(obj['scores'])):
                                        temps[j].append(obj['scores'][j][i])
                            for temp in temps:
                                ar = np.array(temp)
                                vec.append(np.mean(ar, axis=0))
                                vec.append(np.std(ar, axis=0))
                            #Adding the scores of considering text
                            for scores in obj['scores']:
                                vec.append(scores[idx])
                            pos.append(vec)
                if name in obj['negative']: #all objects should have negative, why some don't???
                    neg_indices = obj['negative'][name]
                    for idx in neg_indices:
                        text = obj['text'][idx]
                        if text not in set_neg:
                        #make sure that a negative example is not considered twice.  
                            #compute the avg and std of the surrounding
                            vec = []
                            set_neg.add(text)
                            temps = [] #Use to store intermediate scores for computing avg and std
                            for j in range(len(obj['scores'])):
                                temps.append([])
                            for i in range(idx-opts.windown_size, idx+opts.windown_size+1):
                                if i == idx:
                                    continue
                                if (i < 0)|(i>=len(obj['scores'][0])):
                                    for temp in temps:
                                        temp.append(-1)
                                else:
                                    for j in range(len(obj['scores'])):
                                        temps[j].append(obj['scores'][j][i])
                            for temp in temps:
                                ar = np.array(temp)
                                vec.append(np.mean(ar, axis=0))
                                vec.append(np.std(ar, axis=0))
                            #Adding the scores of considering text
                            for scores in obj['scores']:
                                vec.append(scores[idx])
                            neg.append(vec)

    neg2pos_ratio = 1 #neg examples are twice pos ones
    train2all_ratio= 0.5 #20

    data_train, data_test  = utils.prepare_data_byvector(pos, neg, neg2pos_ratio, train2all_ratio)
    X_train = data_train.data
    X_test = data_test.data
    y_train, y_test = data_train.target, data_test.target
    print(X_train[30000])
    print(y_train[30000])
    print(X_test[20000])
    print(y_test[20000])
    clf = LinearSVC(loss='l2', penalty='l2', dual=False, tol=1e-3) 
    benchmark(clf, X_train, y_train, X_test, y_test, opts)
    
    if opts.model_file:
        with open(opts.model_file, "wb") as f:
            pickle.dump(clf, f)


def main():
    ###############################################################################
    # Load some categories from the training set
    opts = get_parameters()
    if opts.action == "train":
        train(opts)
    if opts.action == "predict":
        classify(opts)
    if opts.action == "boost":
        boost(opts)
    if opts.action == "boost_avg":
        boost_avg(opts)
 
if __name__=="__main__":
    main()

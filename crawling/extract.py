'''
Extract structured data from web pages that do not have schema.org
'''
import sys
import json
import traceback
import os
sys.path.append("../")
from htmlextract import HTMLExtract
from HTMLParser import HTMLParser
from multiprocessing import Pool, cpu_count
import pickle
unescape = HTMLParser().unescape
import numpy as np
import re

pattern = re.compile('[\W_]+')
def preprocess_text(text):
    #- lowercase
    #- strip everything but numbers and chars

    #- lowercase
    clean_text = text.lower()
    #- strip everything but numbers and chars
    clean_text = pattern.sub(' ', clean_text)

    return clean_text

def normalize_str(s):
    return s.strip().lower()

def sen2vec(model1_list, sentences):
    scores = [] 
    processed_sentences = []
    for s in sentences:
        s = preprocess_text(s)
        s = s.strip()
        if len(s) > 0:
            processed_sentences.append(s) 
        
    for name, model, vect in model1_list:
        vec = vect.transform(processed_sentences)
        score = model.decision_function(vec)
        scores.append(score.tolist())
    scores = np.array(scores)
    reverse_scores = np.transpose(scores)
    return processed_sentences, reverse_scores


def read_prop_names(prop_names_file):
    names = []
    with open(prop_names_file) as lines:
        for line in lines:
            names.append(line.strip())
    return names
   
def detect(model1_list, model2_list, html):
    html = unescape(html)
    e = HTMLExtract()
    e.parse(html)
    sentences = e.extract(['p', 'li', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'td'],
    ['script', 'style', 'noscript'])
    labels = []
    threshold = 0
    processed_sentences, s_scores = sen2vec(model1_list, sentences)

    w_size = 15
    for i, scores in enumerate(s_scores):
        #scores is scores for each sentence []
        vec = []
        temps = []
        for x in range(len(scores)):
            temps.append([])
        for j in range(i-w_size, i+w_size+1):
            if j == i:
                continue
            if (j >=0) & (j<s_scores.shape[0]):
                for k, score in enumerate(s_scores[j]):
                    #for each setence in the window area
                    temps[k].append(score)
            else:
                for k, score in enumerate(s_scores[0]):
                    temps[k].append(-1)
        for temp in temps:
            ar = np.array(temp)
            #print ar.shape
            #print ar
            vec.append(np.mean(ar, axis=0))
            vec.append(np.std(ar, axis=0))
        for score in scores:
            vec.append(score)

        max_score = -10
        label = None
        for [name, model] in model2_list:
           score =  model.decision_function([vec])
           score = score[0]
           if (score > max_score) & (score > threshold):
               max_score = score
               label = name 
        if label:
            if label == "ingredients":
                print processed_sentences[i]
            labels.append(label)

    if len(labels) == 0:
        labels = None
    return labels

def load_models(model1_dir, model2_dir):
    prop_names_file = "../recipe_prop_names.txt"
    prop_names = read_prop_names(prop_names_file)
    model1_list = []
    model2_list = []
    for name in prop_names:
        model1_file = model1_dir + "/" + name + ".model"
        if os.path.exists(model1_file):
            vect1_file = model1_dir + "/" + name + ".vect"
            model1 = pickle.load(open(model1_file, "rb"))
            print "Loaded " + model1_file
            vect1 = pickle.load(open(vect1_file, "rb"))
            print "Loaded " + vect1_file

            model1_list.append([name, model1, vect1])

            model2_file = model2_dir + "/" + name + ".model"
            model2 = pickle.load(open(model2_file, "rb"))
            print "Loaded " + model2_file
            model2_list.append([name, model2])

    return model1_list, model2_list

RECIPE = re.compile("recipe", re.IGNORECASE)
def main():
    model1_files = []
    model2_files = []
    model1_dir = "../recipe_data/model_round1"
    model2_dir = "../recipe_data/model_round2"
    datadir = "/san_data/research/kien/structured_data_classification/data_collection/dmoz/data/old-data/html"
    #datadir = sys.argv[1]

    model1_list, model2_list = load_models(model1_dir, model2_dir) 
    files = os.listdir(datadir)
    all = 0
    hit = 0
    re = 0
    for f in files:
        with open(datadir + "/" + f) as lines:
            for line in lines:
                all += 1
                match = RECIPE.search(line)
                if match:
                    re += 1
                    obj = json.loads(line)
                    html = obj['text']
                    url = obj['url']
                    labels = detect(model1_list, model2_list, html)
                    if labels:
                        if "ingredients" in labels:
                            hit += 1
                            labels.append(url)
                            print labels
                            print hit, re, all

main()

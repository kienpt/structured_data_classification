import numpy as np
import re
import itertools
from collections import Counter
from sklearn.preprocessing import LabelBinarizer
import csv
import traceback
from nltk.corpus import stopwords
import json
from sklearn.utils import check_random_state

cachedStopWords = stopwords.words("english")

def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

def clean_str1(text):
    #- lowercase
    #- strip everything but numbers and chars

    #- lowercase
    clean_text = text.lower()
    #- strip everything but numbers and chars
    clean_text = pattern.sub(' ', clean_text)

    return clean_text

def remove_stopword(text):
    text = text.split()
    words = []
    for w in text:
        if w not in cachedStopWords:
            words.append(w)
    return ' '.join(words)

def split_data_pos_neg(x_pos, x_neg, neg2pos_ratio, train2all_ratio):
    #Ajust ratio between positive and negative examples
    #shuffle negative examples
    random_state = check_random_state(100)
    indices = np.arange(x_neg.shape[0])
    random_state.shuffle(indices)
    x_neg = np.array(x_neg, dtype=object)
    x_neg = x_neg[indices]
        
    #Adjust the negative examples size based on the ratio
    max_neg = x_pos.shape[0]*neg2pos_ratio
    x_neg = x_neg[:max_neg]

    y_neg = np.array([[0, 1] for i in range(x_neg.shape[0])])
    y_pos = np.array([[1, 0] for i in range(x_pos.shape[0])])

    x = np.concatenate((x_pos,x_neg), axis=0)
    y = np.concatenate((y_pos,y_neg), axis=0)
    
    #shuffle
    random_state = check_random_state(100)
    indices = np.arange(x.shape[0])
    random_state.shuffle(indices)
    y = y[indices]
    x = x[indices]

    split_point = int(y.shape[0] * train2all_ratio)

    x_train = x[:split_point]
    y_train = y[:split_point]
    x_test = x[split_point:]
    y_test = y[split_point:]
    
    return x_train, y_train, x_test, y_test

def load_data_and_labels_w2v(name):
    """
    """
    #Loading data
    windown_size = 15
    pad_value = -1
    infile = "recipe_index_predicted.json"
    pos = []
    neg = []
    #name = "ingredients"
    set_pos = set([])
    set_neg = set([])

    with open(infile) as lines:
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
                            for i in range(idx-windown_size, idx+windown_size+1):
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
                            for i in range(idx-windown_size, idx+windown_size+1):
                                if (i < 0)|(i>=len(obj['scores'][0])):
                                    vec = vec + [-1] * len(obj['scores'])
                                else:
                                    for scores in obj['scores']:
                                        vec.append(scores[i])
                            neg.append(vec)
    pos = np.array(pos)
    neg = np.array(neg)
    neg2pos_ratio = 1 #neg examples are twice pos ones
    train2all_ratio= 0.5 #20

    x_train, y_train, x_test, y_test = split_data_pos_neg(pos, neg, neg2pos_ratio, train2all_ratio)

    return x_train, y_train, x_test, y_test

def load_data_and_labels():
    """
    Returns split sentences and labels.
    """
    infile = "../../data/acaps/shuffle_acaps.csv"
    # Load data from files
    f = open(infile, 'rb')
    rows = csv.reader(f)
    idx = 7
    label_index = 9#9 is type and 10 is subtype
    x_text = []
    y = []
    for row in rows:
        if row[idx].strip() != "":
            try:
                text = row[idx].lower().strip()
                label = row[label_index].lower().strip()
                if (text != "") & (label != ""):
                    text = text.decode('latin-1')
                    #text = clean_str1(text)
                    text = clean_str(text)
                    text = remove_stopword(text)
                    text = [w.strip() for w in text.split()]
                    x_text.append(text)
                    y.append(label)
            except:
                traceback.print_exc()

    y = LabelBinarizer().fit_transform(y) 
    return [x_text, y]

def pad_sentences(sentences, padding_word="<PAD/>"):
    """
    Pads all sentences to the same length. The length is defined by the longest sentence.
    Returns padded sentences.
    """
    sequence_length = max(len(x) for x in sentences)
    padded_sentences = []
    for i in range(len(sentences)):
        sentence = sentences[i]
        num_padding = sequence_length - len(sentence)
        new_sentence = sentence + [padding_word] * num_padding
        padded_sentences.append(new_sentence)
    return padded_sentences


def build_vocab(sentences):
    """
    Builds a vocabulary mapping from word to index based on the sentences.
    Returns vocabulary mapping and inverse vocabulary mapping.
    """
    # Build vocabulary
    word_counts = Counter(itertools.chain(*sentences))
    # Mapping from index to word
    vocabulary_inv = [x[0] for x in word_counts.most_common()]
    vocabulary_inv = list(sorted(vocabulary_inv))
    # Mapping from word to index
    vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
    return [vocabulary, vocabulary_inv]


def build_input_data(sentences, labels, vocabulary):
    """
    Maps sentencs and labels to vectors based on a vocabulary.
    """
    x = np.array([[vocabulary[word] for word in sentence] for sentence in sentences])
    y = np.array(labels)
    return [x, y]


def load_data(w2v, prop_name):
    """
    Loads and preprocessed data for the MR dataset.
    Returns input vectors, labels, vocabulary, and inverse vocabulary.
    """
    # Load and preprocess data
    if (w2v):
        print "Using word embedding"
        x_train, y_train, x_test, y_test = load_data_and_labels_w2v(prop_name)
        return [x_train, y_train, x_test, y_test]
    else:
        '''  
        sentences, labels = load_data_and_labels()
        sentences_padded = pad_sentences(sentences)
        vocabulary, vocabulary_inv = build_vocab(sentences_padded) #vocabulary_inv has not been used yet
        x, y = build_input_data(sentences_padded, labels, vocabulary)
        return [x, y, len(vocabulary)]
        '''
        return None

def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int(len(data)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]

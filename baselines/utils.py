import re 
pattern = re.compile('[\W_]+')

def preprocess_text(text):
    #- lowercase
    #- strip everything but numbers and chars

    #- lowercase
    clean_text = text.lower()
    #- strip everything but numbers and chars
    clean_text = pattern.sub('', clean_text)

    return clean_text

def fetch_data(indir, label='positive', y_value=1):
    # return data with appropriate label
    # read and preprocess text, then assign label
    print ""

def split_train_test(positive_data, negative_data, ratio=0.5):
    # return train and test data
    print ""


def prepare_data(positive_dir, negative_dir):
    positive_data = fetch_data(positive_dir, 'positive', 1)
    negative_data = fetch_data(negative_dir, 'negative', -1)
    data_train, data_test = split_train_test(positive_data, negative_data, 0.5)
    return data_train, data_test

def test():
    print preprocess_text("aDKJJGEflkk323*6ld^^^j")

test()

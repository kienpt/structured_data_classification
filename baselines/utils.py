

def preprocess_text(text):
    return text

def fetch_data(indir, label='positive', y_value=1):
    # return data with appropriate label
    # read and preprocess text, then assign label

def split_train_test(positive_data, negative_data, ratio=0.5):
    # return train and test data


def prepare_data(positive_dir, negative_dir):
    positive_data = fetch_data(positive_dir, 'positive', 1)
    negative_data = fetch_data(negative_dir, 'negative', -1)
    data_train, data_test = split_train_test(positive_data, negative_data, 0.5)
    return data_train, data_test


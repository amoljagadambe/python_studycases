"""
Referred from Github https://github.com/Meghana-Meghana/Sentiment-Analysis
"""

from keras.preprocessing.text import Tokenizer
import numpy as np
import pandas as pd
import os
from nltk.corpus import stopwords
import string
from collections import Counter
from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model
import csv

BASE_DIR = os.getcwd()
train_data_set_path = os.path.join(BASE_DIR, 'train_data.csv')
test_data_set_path = os.path.join(BASE_DIR, 'sentiment-eval.csv')


def load_file(filepath):
    file = open(filepath, 'r')  # open the file in the read only mode
    text = file.read()  # read the contents of the file
    file.close()  # close the file
    return text


def clean_file(file):
    tokens = file.split()  # split into tokens on whitespace

    table = str.maketrans('', '', string.punctuation)  # remove punctuation
    tokens = [w.translate(table) for w in tokens]

    tokens = [word for word in tokens if word.isalpha()]  # remove non-alphabetic tokens

    set_of_stop_words = set(stopwords.words('english'))  # remove stop words
    tokens = [word for word in tokens if not word in set_of_stop_words]

    tokens = [word for word in tokens if len(word) > 1]  # remove tokens of length <= 1

    return tokens


col_list = ["text"]


def add_words_to_vocab_and_update_count(directory, vocab):
    df = pd.read_csv(directory, usecols=col_list)
    for index, row in df.iterrows():
        tokens = clean_file(row['text'])  # clean the file
        vocab.update(tokens)


vocab = Counter()
add_words_to_vocab_and_update_count(train_data_set_path, vocab)
print(len(vocab))

tokens = [token for token, count in vocab.items()]


def save_list(lines, filename):
    data = '\n'.join(lines)
    file = open(filename, 'w')
    file.write(data)
    file.close()


save_list(tokens, 'vocab.txt')


def reviews_to_lines(directory, vocab):
    lines = []
    df = pd.read_csv(directory, usecols=col_list)
    for index, row in df.iterrows():
        tokens = clean_file(row['text'])  # clean the file
        tokens = [word for word in tokens if word in vocab]  # filter by vocab
        line = ' '.join(tokens)  # single review -> tokens -> filter -> single line with tokens spaced by whitespace
        lines.append(line)  # list of reviews. Single review is stored at each index of the list
    return lines


# load the vocabulary
vocab = load_file("vocab.txt")
vocab = vocab.split()
vocab = set(vocab)

train_reviews = reviews_to_lines(train_data_set_path, vocab)
test_reviews = reviews_to_lines(test_data_set_path, vocab)


# print(len(train_reviews))
# print(len(test_reviews))


def prepare_data(train_reviews, test_reviews, mode):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(train_reviews)  # fit the tokenizer on the texts

    xtrain = tokenizer.texts_to_matrix(train_reviews, mode=mode)  # encode the training set
    xtest = tokenizer.texts_to_matrix(test_reviews, mode=mode)  # encode the test set

    return xtrain, xtest


xtrain, xtest = prepare_data(train_reviews, test_reviews, mode='freq')
print(" Shape of xtrain: ", xtrain.shape)
print(" Shape of xtest : ", xtest.shape)

'''
Convert labels into numpy array with one hot encoding
'''


label_list = ["label"]
df = pd.read_csv(train_data_set_path, usecols=label_list)
conv_arr = df.values
arr1 = np.delete(conv_arr, [1, 2], axis=1)

# converting into 1D array
arr1 = arr1.ravel()
a = np.array(arr1)
ytrain = np.where(a == 'Positive', 0, 1)


'''
MODEL CREATION
'''


def train_seniment_analysis_model(xtrain, ytrain):
    n_words = xtrain.shape[1]
    # define the network
    model = Sequential()
    model.add(Dense(50, input_shape=(n_words,), activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # compile the network
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # fit the network to the training data
    history = model.fit(xtrain, ytrain, epochs=80, verbose=2)
    # save model and architecture to single file
    model.save("model.h5")
    print("Saved model to disk")

    return model, history


classifier, model_history = train_seniment_analysis_model(xtrain, ytrain)


def predict_sentiment_model():
    # load model
    model = load_model('model.h5')
    # make a prediction
    ytest = model.predict_classes(xtest)
    with open('output_label.csv', mode='w') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(['ID', 'Label'])
        # show the inputs and predicted outputs
        for i in range(len(ytest)):
            if ytest[i] == 0:
                employee_writer.writerow([i, 'Positive'])
            else:
                employee_writer.writerow([i, 'Negative'])


predict_sentiment_model()
import os
import numpy
from sklearn.linear_model import LogisticRegression
import pickle

base_dir = os.getcwd()
data_file_path = os.path.join(base_dir, 'chinese_text')
encoding = 'big5hkscs'

lines = []
num_errors = 0

for line in open(data_file_path + '/training.txt', 'rb'):
    try:
        lines.append(line.decode(encoding).split())
    except UnicodeDecodeError as e:
        num_errors += 1

print('Encountered %d decoding errors.' % num_errors)

vocabulary = set()

for data in lines:
    for word in data:
        vocabulary.add(word)

print(len(vocabulary))

four_gram_word = []
for word in vocabulary:
    if len(word) == 4:
        four_gram_word.append(word)


def store_vocab_file(vocab: set):
    try:
        with open(base_dir + '/vocabulary.txt', 'w', encoding=encoding) as cursor:
            for val in vocab:
                cursor.write(val + '\n')
    except FileNotFoundError:
        return False


feature_maps = []
for grams in four_gram_word:
    first, second, third, fourth = grams
    feature_maps.append((first + second, second + third, third + fourth, second, third))
print(len(four_gram_word))
print(len(feature_maps))

print(feature_maps[:10])

len_vocab = len(feature_maps)

vocabulary_list = list(vocabulary)

index_mapping = []
for grams_data in feature_maps:
    index_for_single = []
    for single_gram in grams_data:
        if single_gram in vocabulary_list:
            index_for_single.append(vocabulary_list.index(single_gram))
        else:
            index_for_single.append(0)
    index_mapping.append(index_for_single)

print(index_mapping)

labels = []
for indexes in index_mapping:
    if sum(indexes) == 0:
        labels.append(0)
    else:
        labels.append(1)

print(labels)

np_array = numpy.asarray(index_mapping)
x_features = np_array / len_vocab

# Logistic model
logistic_model = LogisticRegression()

# train the model
logistic_model.fit(x_features, labels)

# save the model
filename = base_dir + '/logistic_model.sav'
pickle.dump(logistic_model, open(filename, 'wb'))


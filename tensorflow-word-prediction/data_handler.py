import string
import os

BASE_FOLDER = os.path.abspath(os.path.dirname(__name__))
with open(BASE_FOLDER + "/dataset/dataset.txt", 'r') as f:
    data = f.read()
    data_list = data.split('\n')

# print(data_list[253:300])
data_list = data[253:]  # actual Play Start from line Number 253 so setting the intial point to start
data_list = " ".join(data)


class DatasetCleaner:

    def clean_text(self, doc):
        tokens = doc.split()
        table = str.maketrans('', '', string.punctuation)
        tokens = [w.translate(table) for w in tokens]
        tokens = [word for word in tokens if word.isalpha()]
        tokens = [word.lower() for word in tokens]
        return tokens

    def line_converter(self, tokens):
        length = 50 + 1
        lines = []

        for i in range(length, len(tokens)):
            seq = tokens[i - length:i]
            line = ' '.join(seq)
            lines.append(line)
            if i > 200000:
                break
        return lines

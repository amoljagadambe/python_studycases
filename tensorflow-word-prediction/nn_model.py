from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,LSTM,Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
from .data_handler import DatasetCleaner
from .data_handler import data_list
from .net_handler import nethandler
import numpy as np


class neuralNet:
    def __init__(self):
        tokenizer = Tokenizer()
        out_obj = DatasetCleaner()
        tokens = out_obj.clean_text(data_list)
        lines = out_obj.line_converter(tokens)
        tokenizer.fit_on_texts(lines)
        sequences = tokenizer.texts_to_sequences(lines)

        sequences = np.array(sequences)
        print(sequences[0:50])
        X, y = sequences[:, :-1], sequences[:, -1]
        self.vocab_size = len(tokenizer.word_index) + 1
        self.y = to_categorical(y, num_classes=self.vocab_size)
        self.seq_length = X.shape[1]

    def trainnet(self):
        model = Sequential()
        model.add(Embedding(self.vocab_size, 50, input_length=self.seq_length))
        model.add(LSTM(100, return_sequences=True))
        model.add(LSTM(100))
        model.add(Dense(100, activation='relu'))
        model.add(Dense(self.vocab_size, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(self.X, self.y, batch_size=256, epochs=100)

        nethandler().savenet(model=model)

    def generate_text_seq(model, tokenizer, text_seq_length, seed_text, n_words):
        text = []

        for _ in range(n_words):
            encoded = tokenizer.texts_to_sequences([seed_text])[0]
            encoded = pad_sequences([encoded], maxlen=text_seq_length, truncating='pre')

            y_predict = model.predict_classes(encoded)

            predicted_word = ''
            for word, index in tokenizer.word_index.items():
                if index == y_predict:
                    predicted_word = word
                    break
            seed_text = seed_text + ' ' + predicted_word
            text.append(predicted_word)
        return ' '.join(text)

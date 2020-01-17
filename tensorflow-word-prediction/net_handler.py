from tensorflow.python import keras
import os

BASE_FOLDER = os.path.abspath(os.path.dirname(__name__))
NEXT_PATH = "/tensorflow-word-prediction/saved-model/"
FULL_PATH = BASE_FOLDER + NEXT_PATH


class nethandler:
    def __init__(self):
        print("Store Model init")

    def savenet(self, model=None):
        model_json = model.to_json()
        with open(FULL_PATH+"model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        model.save(FULL_PATH + "model.h5")

    def loadnet(self):

        loaded_model = keras.models.load_model(FULL_PATH + "model.h5")
        print("Loaded model from disk")

        return loaded_model

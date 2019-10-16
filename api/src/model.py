from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import ModelCheckpoint
import numpy as np
import pandas as pd

def load_model(fileName):
    from keras.models import model_from_json
    json_file = open(fileName+".json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(fileName+".h5")
    loaded_model.compile(loss="mse", optimizer="adam", metrics=['mse', 'mae'])
    return loaded_model

def test(model):
    print("INPUT CPU : ( 0 ~ 100 )")
    cpu = input()
    print("INPUT MEMORY : ( 0 ~ 100 )")
    memory = input()
    print("INPUT STORAGE : ( 0 ~ 100 )")
    storage = input()
    print("INPUT RATING : ( 0 ~ 100 )")
    rating = input()
    y = model.predict(np.array([cpu,memory,storage,rating]).reshape(1,4))
    print(y)

def predict(cpu, memory, storage, rating, model):
    y = model.predict(np.array([cpu, memory, storage, rating]).reshape(1, 4))
    print(y)
    return y[0][0], y[0][1], y[0][2]

if __name__ == '__main__':
    model = load_model("model")
    print(predict(10,10,10,10,model))
    #test(model)





#include necessary libraries
from keras import backend as K

from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants, signature_def_utils_impl

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

class neural_net:
    def feedforward(self,hidden_list,inp,activation_list,lr,optimiser):
        if len(hidden_list) != len(activation_list):
            return ArithmeticError
        model = Sequential()
        model.add(Dense(hidden_list[0], input_dim=inp))
        model.add(Activation(activation_list[0]))
        for i in range(1,len(hidden_list)):
            model.add(Dense(hidden_list[i]))
            model.add(Activation(activation_list[i]))
        return model

    def rnn(self,):

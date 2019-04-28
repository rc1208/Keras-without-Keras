#import the necessary libraries
import tensorflow as tf
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

#set tensorflow session

sess = tf.Session()
K.set_session(sess)
K.set_learning_phase(0)



model_version = "1"
epoch = 10

#read the data
data = pd.read_csv('../../../data/datatraining.txt')
X = data[['Humidity', 'Light', 'CO2', 'HumidityRatio', 'Temperature']].values
y = data['Occupancy'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
print("len of train=", len(X_train))
#example test data - 23,27.125,419,686,0.00471494214590473


#build the model
model = Sequential()
model.add(Dense(8, input_dim=5))
model.add(Activation('tanh'))
model.add(Dense(1))
model.add(Activation('sigmoid'))
sgd = SGD(lr=0.1)

model.compile(loss='binary_crossentropy', optimizer=sgd)
model.fit(X_train, y_train, batch_size=1000, nb_epoch=epoch, verbose = 2)

#get tensorflow serving input and output variable
x = model.input
y = model.output
prediction_signature = tf.saved_model.signature_def_utils.predict_signature_def({"inputs": x}, {"prediction":y})

#test if prediction sig is is valid

valid_prediction_signature = tf.saved_model.signature_def_utils.is_valid_signature(prediction_signature)

print(prediction_signature)

if(valid_prediction_signature == False):
    raise ValueError("Error: Prediction signature not valid!")

#build and configure model
builder = saved_model_builder.SavedModelBuilder('../models/feeds/'+model_version)
legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
builder.add_meta_graph_and_variables(
      sess, [tag_constants.SERVING],
      signature_def_map={
           signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:prediction_signature,
      },
      legacy_init_op=legacy_init_op)


#save model
builder.save()

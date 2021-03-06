from flask import Flask
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow_serving.model_volume.neural_nets.feed as feed
import tensorflow_serving.model_volume.neural_nets.rnn as rnn
import tensorflow_serving.model_volume.neural_nets.cnn as cnn
from keras.datasets import mnist
from keras.utils import np_utils
from keras.utils import to_categorical
import numpy as np
app = Flask(__name__)
import pickle
import gzip
import datetime

folder = "tensorflow_serving/model_volume/models/"
model_version = "1.0"


def create_feed_forward(content,callback_log_dir):
    #suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    #callback_log_dir = callback_log_dir +  "/" + suffix + "_callback_log_feed.csv"
    #print(callback_log_dir)
    ff = feed.feedforward_nn()
    ff.design_model(content['hidden_list'],content['inp'],content['activation_list'])
    ff.model_compile(content['optimiser'],content['loss_function'])
    data = pd.read_csv(content['data_location'])
    collist = data.columns.tolist()
    X = data[collist[0:-1]].values
    y = data[collist[-1:]].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=float(content['split_value']))
    ff.model_train(X_train, y_train, X_test, y_test, content['epochs'],callback_log_dir)
    ff.model_save(folder + "feeds",model_version )
    return callback_log_dir


def clean_test_data(loc):
    data = open(loc).read().lower()
    chars = sorted(list(set(data)))
    char_to_int = dict((c, i) for i, c in enumerate(chars))
    n_chars = len(data)
    n_vocab = len(chars)
    seq_length = n_vocab
    dataX = []
    dataY = []
    for i in range(0, n_chars - seq_length, 1):
        seq_in = data[i:i + seq_length]
        seq_out = data[i + seq_length]
        dataX.append([char_to_int[char] for char in seq_in])
        dataY.append(char_to_int[seq_out])
    n_patterns = len(dataX)
    X = np.reshape(dataX, (n_patterns, seq_length, 1))
    X = X / float(n_vocab)
    y = np_utils.to_categorical(dataY)
    return X,y


def create_rnn(content,callback_log_dir):
    #suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    #callback_log_dir = callback_log_dir +  "/" + suffix + "_callback_log_rnn.csv"
    r = rnn.rnn()
    X,y = clean_test_data(content['data_location'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=float(content['split_value']))
    r.design_model(y_train.shape[1],content['lstm_out'],content['dense_out'],content['reg_dropout'],X_train.shape[1],X_train.shape[2])
    r.model_compile(content['optimiser'], content['loss_function'])
    r.model_train(X_train, y_train, X_test, y_test,content['epochs'], content['batch_size'], callback_log_dir)
    r.model_save(folder + "rnn",model_version )

    return callback_log_dir


def create_cnn(content,callback_log_dir):
    #suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    #callback_log_dir = callback_log_dir +  "/" + suffix + "_callback_log_cnn.csv"
    c = cnn.cnn()
    #design_model(self,hidden_list,inp,activation_list,kernel_size_1,kernel_size_2)
    c.design_model(content['hidden_list'],content['width'],content['height'],content['activation_list'],content['kernel_size'])
    #model_compile(self,optimizer,loss)
    c.model_compile(content['optimiser'],content['loss_function'])
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    #loading the data -- install mlxtend for this
    data = pickle.load(gzip.open(content['data_location'],'rb'))
    X = data[0]
    y = data[1]
    #print("hello cnn")

    split_value = int((1 - float(content['split_value']) * len(X)))
    X_train = X[:split_value,:,:]
    X_test = X[split_value:,:,:]

    y_train = y[:split_value,:]
    y_test = y[split_value:,:]

    #reshape X_train and X_test
    X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],X_train.shape[2],1)
    X_test = X_test.reshape(X_test.shape[0],X_test.shape[1],X_test.shape[2],1)


    #one-hot encode target column
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)


    c.model_train(X_train, y_train, X_test, y_test,content['epochs'],callback_log_dir)
    c.model_save(folder + "cnn",model_version )

    return callback_log_dir

if __name__ == "__main__":
    app.run()

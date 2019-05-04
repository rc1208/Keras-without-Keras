from flask import Flask, request
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow_serving.model_volume.neural_nets.feed as feed
import tensorflow_serving.model_volume.neural_nets.rnn as rnn
app = Flask(__name__)
import os
print(os.path)
folder = "tensorflow_serving/model_volume/models/"
model_version = "1.0"

def create_feed_forward(content):
    ff = feed.feedforward_nn()
    ff.design_model(content['hidden_list'],content['inp'],content['activation_list'])
    ff.model_compile(content['optimiser'],content['loss_function'])
    data = pd.read_csv(content['data_location'])
    collist = data.columns.tolist()
    X = data[collist[0:-1]].values
    y = data[collist[-1:]].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=float(content['split_value']))
    ff.model_train(X_train, y_train, X_test, y_test)
    ff.model_save(folder + "feeds",model_version )

def create_rnn(content):
    r = rnn.rnn()
    r.design_model(content['vocab_size'],content['output_d'],content['max_len'],content['lstm_out'],content['lstm_drop'],content['lstm_recc_drop'],content['dense_out'],content['reg_dropout'])
    r.model_compile(content['optimiser'],content['loss_function'])
    data = ""
    

def create_cnn(content):
    pass

@app.route("/",methods=['POST'])
def handler():
    content = request.get_json()
    if content['nn_type'] == 'feedforward':
        create_feed_forward(content)
    elif content['nn_type'] == 'rnn':
        create_rnn(content)
    elif content['nn_type'] == 'cnn':
        create_cnn(content)
    else:
        return 'error!!!!'


if __name__ == "__main__":
    app.run()

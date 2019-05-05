import tensorflow_serving.model_volume.neural_nets.feed as feed
import tensorflow_serving.model_volume.neural_nets.rnn as rnn
import tensorflow_serving.model_volume.neural_nets.cnn as cnn
import unittest
import pandas as pd
from sklearn.model_selection import train_test_split
import os

class NeuralNetTest(unittest.TestCase):
    def setUp(self):
        self.forward = feed.feedforward_nn()
        self.rnn = rnn.rnn()
        self.cnn = cnn.cnn()

    def testFeedDesign(self):
        hidden_layers = "5 5 1"
        inp = "5"
        activation_layer = "relu relu sigmoid"
        self.forward.design_model(hidden_layers,inp,activation_layer)
        ret_val = self.forward.model.get_config()
        self.assertEqual(ret_val[0]['class_name'],'Dense')
        self.assertEqual(ret_val[0]['config']['units'],5)

        self.assertEqual(ret_val[1]['class_name'], 'Activation')
        self.assertEqual(ret_val[1]['config']['activation'], 'relu')

        self.assertEqual(ret_val[2]['class_name'], 'Dense')
        self.assertEqual(ret_val[2]['config']['units'], 5)

        self.assertEqual(ret_val[3]['class_name'], 'Activation')
        self.assertEqual(ret_val[3]['config']['activation'], 'relu')

        self.assertEqual(ret_val[4]['class_name'], 'Dense')
        self.assertEqual(ret_val[4]['config']['units'], 1)

        self.assertEqual(ret_val[5]['class_name'], 'Activation')
        self.assertEqual(ret_val[5]['config']['activation'], 'sigmoid')

    def testFeedTrain(self):
        hidden_layers = "5 5 1"
        inp = "5"
        activation_layer = "relu relu sigmoid"
        self.forward.design_model(hidden_layers, inp, activation_layer)
        self.forward.model_compile('adam', 'binary_crossentropy')
        data = pd.read_csv('feed_test.csv')
        collist = data.columns.tolist()
        X = data[collist[0:-1]].values
        y = data[collist[-1:]].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        self.forward.model_train(X_train, y_train, X_test, y_test, '5', "feed.csv")
        ret = pd.read_csv('feed.csv')
        self.assertIsNotNone(ret)

    def testRnnDesign(self):



if __name__ == "__main__":
    unittest.main()
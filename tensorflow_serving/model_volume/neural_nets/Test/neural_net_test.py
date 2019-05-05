import tensorflow_serving.model_volume.neural_nets.feed as feed
import tensorflow_serving.model_volume.neural_nets.rnn as rnn
import tensorflow_serving.model_volume.neural_nets.cnn as cnn
import unittest

class NeuralNetTest(unittest.TestCase):
    def __init__(self):
        self.forward = feed.feedforward_nn()
        self.rnn = rnn.rnn()
        self.cnn = cnn.cnn()

    def testFeedDesign(self):
        hidden_layers = "5 5 1"
        inp = "5"
        activation_layer = "relu relu sigmoid"
        self.forward.design_model(hidden_layers,inp,activation_layer)
        print(self.forward.model.get_config())
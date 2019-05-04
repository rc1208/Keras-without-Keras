# credits: https: https://towardsdatascience.com/building-a-convolutional-neural-network-cnn-in-keras-329fbbadc5f5
from keras.datasets import mnist
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants
import tensorflow as tf
#download mnist data and split into train and test sets
(X_train, y_train), (X_test, y_test) = mnist.load_data()


#reshape data to fit model
X_train = X_train.reshape(60000,28,28,1)
X_test = X_test.reshape(10000,28,28,1)


from keras.utils import to_categorical
#one-hot encode target column
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)


from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten

class cnn:

    def __init__(self):
        #create model
        self.model = Sequential()
    def design_model(self,hidden_list,inp,activation_list,kernel_size_1,kernel_size_2):

        #add model layers
        self.model.add(Conv2D(hidden_list[0], kernel_size=kernel_size_1, activation=activation_list[0], input_shape=(inp,inp,1)))
        self.model.add(Conv2D(hidden_list[1], kernel_size=kernel_size_2, activation=activation_list[1]))
        self.model.add(Flatten())
        self.model.add(Dense(hidden_list[2], activation=activation_list[2]))


    def model_train(self,X_train, y_train, X_test, y_test,epochs):
        #train the model
        self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs)

    def model_compile(self,optimizer,loss):
        #compile model using accuracy to measure model performance
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    def model_predict(self):

        #predict first 4 images in the test set
        self.model.predict(X_test[:4])

    def model_save(self,folder,model_version):
        sess = tf.Session()
        x = self.model.input
        y = self.model.output
        prediction_signature = tf.saved_model.signature_def_utils.predict_signature_def({"inputs": x},{"prediction": y})
        valid_prediction_signature = tf.saved_model.signature_def_utils.is_valid_signature(prediction_signature)
        if (valid_prediction_signature == False):
            raise ValueError("Error: Prediction signature not valid!")
        builder = saved_model_builder.SavedModelBuilder(folder + model_version)
        legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
        builder.add_meta_graph_and_variables(
            sess, [tag_constants.SERVING],
            signature_def_map={
                signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: prediction_signature,
            },
            legacy_init_op=legacy_init_op)

        # save model
        builder.save()

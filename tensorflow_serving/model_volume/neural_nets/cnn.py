# credits: https: https://towardsdatascience.com/building-a-convolutional-neural-network-cnn-in-keras-329fbbadc5f5
from keras.datasets import mnist
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants
import tensorflow as tf
from keras.callbacks import CSVLogger
import datetime


from keras.utils import to_categorical

from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten

class cnn:

    def __init__(self):
        #create model
        self.model = Sequential()
    def design_model(self,hidden_list,width,height,activation_list,kernel_size):
        hidden_list = hidden_list.split()
        activation_list = activation_list.split()
        kernel_size = kernel_size.split()

        #add model layers
        self.model.add(Conv2D(int(hidden_list[0]), kernel_size=int(kernel_size[0]), activation=activation_list[0], input_shape=(int(width),int(height),1)))
        for i in range(1,len(hidden_list) - 1):
            self.model.add(Conv2D(int(hidden_list[i]), kernel_size=int(kernel_size[i]), activation=activation_list[i]))
        self.model.add(Flatten())
        self.model.add(Dense(int(hidden_list[-1]), activation=activation_list[-1]))


    def model_train(self,X_train, y_train, X_test, y_test,epochs,logcsv="callback_log.csv"):
        #train the model
        callback = [CSVLogger(filename=logcsv)]
        self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=int(epochs),callbacks=callback)

    def model_compile(self,optimizer,loss):
        #compile model using accuracy to measure model performance
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    def model_predict(self):

        #predict first 4 images in the test set
        self.model.predict(X_test[:4])

    def model_save(self,folder,model_version):
        init_op = tf.global_variables_initializer()
        sess = tf.Session()
        sess.run(init_op)
        x = self.model.input
        y = self.model.output
        prediction_signature = tf.saved_model.signature_def_utils.predict_signature_def({"inputs": x},{"prediction": y})
        valid_prediction_signature = tf.saved_model.signature_def_utils.is_valid_signature(prediction_signature)
        if (valid_prediction_signature == False):
            raise ValueError("Error: Prediction signature not valid!")
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        folder = folder +  model_version + "_" + suffix
        builder = saved_model_builder.SavedModelBuilder(folder)
        #legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
        builder.add_meta_graph_and_variables(
            sess, [tag_constants.SERVING],
            signature_def_map={
                signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: prediction_signature,
            },)
            #legacy_init_op=legacy_init_op)

        # save model
        builder.save()
        sess.close()

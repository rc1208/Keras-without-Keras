from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.callbacks import CSVLogger
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants
import tensorflow as tf
import datetime

class feedforward_nn:

    def __init__(self):
        self.model = Sequential()

    def design_model(self,hidden_layers,inp,activation_layer):
        hidden_list = hidden_layers.split()
        activation_list = activation_layer.split()
        if len(hidden_list) != len(activation_list):
            return ArithmeticError
        self.model.add(Dense(int(hidden_list[0]), input_dim=int(inp)))
        self.model.add(Activation(activation_list[0]))
        for i in range(1,len(hidden_list)):
            self.model.add(Dense(int(hidden_list[i])))
            self.model.add(Activation(activation_list[i]))

    def model_compile(self,optimiser,loss_function):
        self.model.compile(loss=loss_function, optimizer=optimiser, metrics=['accuracy'])

    def model_train(self,X_train,y_train,X_test,y_test, epochs, logcsv="callback_log.csv"):
        callback = [CSVLogger(filename=logcsv)]
        self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=int(epochs), callbacks=callback)

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
        builder.add_meta_graph_and_variables(
            sess, [tag_constants.SERVING],
            signature_def_map={
                signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: prediction_signature,
            },)

        # save model
        builder.save()
        sess.close()

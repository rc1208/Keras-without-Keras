# credits: https: https://towardsdatascience.com/building-a-convolutional-neural-network-cnn-in-keras-329fbbadc5f5
from keras.datasets import mnist
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
        model = Sequential()
    def design_model(self,hidden_list,inp,activation_list,lr,optimiser):

        #add model layers
        model.add(Conv2D(64, kernel_size=3, activation='relu', input_shape=(28,28,1)))
        model.add(Conv2D(32, kernel_size=3, activation='relu'))
        model.add(Flatten())
        model.add(Dense(10, activation='softmax'))


    def model_train(self):
        #train the model
        model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=3)

    def model_compile(self):
        #compile model using accuracy to measure model performance
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    def model_predict(self):

        #predict first 4 images in the test set
        model.predict(X_test[:4])

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

import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Masking, Embedding
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants
from keras.callbacks import CSVLogger

class rnn:
    def __init__(self):
        self.model = Sequential()

    def design_model(self,vocab_size,lstm_out,dense_out,reg_dropout,inp_row,inp_col):
        self.model.add(LSTM(int(lstm_out), return_sequences=False, input_shape=(inp_row, inp_col)))
        self.model.add(Dense(int(dense_out), activation='relu'))
        self.model.add(Dropout(float(reg_dropout)))
        self.model.add(Dense(vocab_size, activation='softmax'))

    def model_compile(self,optimiser,loss_function):
        self.model.compile(optimizer=optimiser, loss=loss_function, metrics=['accuracy'])

    def model_train(self,X_train,y_train,X_test,y_test,ep,batch_size_value,logcsv="callback_log.csv"):
        callback = [CSVLogger(filename=logcsv)]
        self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=int(ep),batch_size=int(batch_size_value),callbacks=callback)

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
        builder = saved_model_builder.SavedModelBuilder(folder + model_version)
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

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Masking, Embedding

class rnn:
    def design_model(self,vocab_size,output_d,max_len):
        model = Sequential()
        model.add(Embedding(input_dim=vocab_size, output_dim=output_d, input_length=max_len))
        model.add(Masking(mask_value=0.0))
        model.add(LSTM(64, return_sequences=False, dropout=0.1, recurrent_dropout=0.1))

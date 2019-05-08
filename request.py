import requests
'''
res = requests.post('http://localhost:3333/api/neural-network/v1.0/', json={"nn_type":"feedforward", \
  "hidden_list":"5 5 1", \
  "inp": "5", \
  "activation_list":"relu relu sigmoid", \
  "optimiser":"adam", \
  "split_value": "0.2", \
  "epochs":"3", \
  "loss_function": "binary_crossentropy", \
  "data_location":"data/data_new.csv"})
if res.ok:
    print(res)



res_cnn = requests.post('http://localhost:3333/api/neural-network/v1.0/', json={"nn_type":"cnn", \
  "hidden_list":"64 32 4", \
  "width": "21",
  "height":"21",
  "kernel_size":"3 3", \
  "activation_list":"relu relu softmax", \
  "epochs":"3", \
  "optimiser":"adam", \
  "split_value": "0.2", \
  "loss_function": "categorical_crossentropy", \
  "data_location":"data/mnist21x21_3789_converted.pklz"})
if res_cnn.ok:
    print("Model Compiled")

'''

res_rnn = requests.post('http://localhost:3333/api/neural-network/v1.0/', json={"nn_type":"rnn",
"lstm_out":"256",
"dense_out":"100",
"reg_dropout":"0.2",
"epochs":"1",
"batch_size":"1000",
"optimiser":"adam",
"split_value": "0.2",
"loss_function": "categorical_crossentropy",
"data_location":"data/cnn-test.txt"})
if res_rnn.ok:
    print("Model Compiled!")

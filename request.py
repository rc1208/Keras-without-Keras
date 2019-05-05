import requests

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
    print("Model Compiled!")

'''

res_cnn = requests.post('http://localhost:3333/api/neural-network/v1.0/', json={"nn_type":"cnn", \
  "hidden_list":"64 32 4", \
  "inp": "21",
  "kernel_size":"3 3", \
  "activation_list":"relu relu softmax", \
  "epochs":"3", \
  "optimiser":"adam", \
  "split_value": "0.2", \
  "loss_function": "categorical_crossentropy", \
  "data_location":"data/mnist21x21_3789_converted.pklz"})
if res_cnn.ok:
    print("Model Compiled!")
'''

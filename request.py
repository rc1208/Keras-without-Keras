import requests
res = requests.post('http://localhost:3333/api/neural-network/v1.0/', json={"nn_type":"feedforward", \
  "hidden_list":"5 5 1", \
  "inp": "5", \
  "activation_list":"relu relu sigmoid", \
  "optimiser":"adam", \
  "split_value": "0.2", \
  "loss_function": "binary_crossentropy", \
  "data_location":"/Users/rahulchowdhury/Documents/Spring-Sem-19/CSCI5922/project/data/data_new.csv"})
if res.ok:
    print("Model Compiled!")

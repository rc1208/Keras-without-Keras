# Keras without Keras

Deep learning has been used in a variety of applications since it was introduced. However, for those who does not know how to code, deep learning is not an available method. We propose a deep learning framework called ‘*Keras* *without* *Keras*’ so that user can use deep learning with their own data, and check the results with various options without any coding knowledge.

<center><img src="https://github.com/rc1208/Keras-without-Keras/blob/master/resources/framework.png" width="40%"></center>

### 1. Objectives

* Provide NN, CNN, RNN functions according to user’s input data. 
* Make user manipulate a visual interface without any coding. Keras code is generated automatically and operated in the backend.
* Provide various options so that user can change them and compare results accordingly.

### 2. Problem

Deep learning libraries require user to handle following steps in programming languages:

* step 1) Import data and split them into training and test sets
* step 2) Build a neural network architecture
* step 3) Train a model, then test it
* step 4) Check results, change options 
* step 5) Go back to step (2) <br>
→ *If you don’t know how to write a program, you can’t use deep learning!*

**Research question:** can we use neural networks including CNN and RNN without knowing how to write a program?

### 3. Architecture
<img src="https://github.com/rc1208/Keras-without-Keras/blob/master/resources/archi.png" width="60%">

***Frontend***
* *Data upload page (html, python)*: receive user’s data and decide a network type (DNN, CNN, RNN)
* *Build a net page (typescript)*: allow user to decide hyper-params, neural net architecture, and pass them to backend

***Backend***
* Generate a Keras code according to inputs (python)
* Send results to frontend

### 4. Result (User's view)
<img src="https://github.com/rc1208/Keras-without-Keras/blob/master/resources/result.png" width="100%">

### 5. How to use

<br><br><br><br>




## Softwares required to be installed: ##

1. Python 3 or >
2. Flask 
3. Docker
4. Tensorflow
5. Tensorflow Serving

#### CURL request for FF NN ####
curl -X POST   http://localhost:8501/v1/models/feeds:predict   -H 'cache-control: no-cache'   -H 'postman-token: f7fb6e3f-26ba-a742-4ab3-03c953cefaf5'   -d '{
 "inputs":[
  [23,27.125,419,686,0.00471494214590473]
  ]
}'

  

#### to generate the sqlite database (instance/data.db), run:
#### Warn: this will remove existing training data inventory saved in instance/data.db, don't do it if there are already some data uploaded
python init_database.py


#### Run python request.py for a sample CURL request to feedforward. Change parameters in JSON as necessary ####



### feed forward POST Json ###


curl -i -H "Content-Type: application/json" -X POST -d \
'{"nn_type":"feedforward", \
  "hidden_list":"5 5 1", \
  "inp": "5", \
  "activation_list":"relu relu sigmoid", \
  "optimiser":"adam", \
  "split_value": "0.2", \
  "loss_function": "binary_crossentropy", \
  "data_location":"data/data_new.csv" \
  }' 'http://localhost:3333/api/neural-network/v1.0/'
  
  
  

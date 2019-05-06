# Keras without Keras

Deep learning has been used in a variety of applications since it was introduced. However, for those who do not know how to code, deep learning is not an available method. We propose a deep learning framework called ‘*Keras* *without* *Keras*’ so that user can use deep learning with their own data, and check the results with various options without any coding knowledge.

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
→ *If you don’t know how to write programs, you can’t use deep learning!*

**Research question:** can we use neural networks including CNN and RNN without knowing how to write a program?

### 3. Architecture
<img src="https://github.com/rc1208/Keras-without-Keras/blob/master/resources/archi.png" width="60%">

***Frontend***
* *Data upload page (html, js, python)*: receive user’s data (tabular, image, text), and decide a network type (DNN, CNN, RNN)
* *Data selection page (html, js, python)*: allow user to retrieve saved data to run again
* *Build a net page (typescript)*: allow user to decide hyper-params, neural net architecture, and pass them to backend

***Backend***
* Generate a Keras code according to inputs (python)
* Train the network to generate the model
* Save the model to disk
* Send results to frontend

### 4. Result (User's view)
<img src="https://github.com/rc1208/Keras-without-Keras/blob/master/resources/result.png" width="100%">

### 5. How to run

1. Initialize the SQlite database -> `python init_database.py`
2. Run the Node Frontend Server
 - `cd playground`
 - Install Dependencies -> `npm i`
 - Compile the app and place it in the dist/ directory -> `npm run build`
 - Open a page on your browser -> `npm run serve`
3. Run the Flask Backend Server
 - To start the server -> `python app.py`
 - Optional Step: If you want to CURL on the models, run -> `python request.py` (Comment out the request that you don't want to test)
4. Some example data for uploading/running test:
 - tabular data: data/data_new.csv (for classification)
 - image data: data/mnist21x21_3789_one_hot.pklz (for image classification)
 - text data: data/asyoulikeit.txt (for language modeling)




## Softwares required to be installed: ##

### Backend Software Requirements ###

| Software      |  Link         | 
| ------------- |:-------------:| 
| Python 3 or > | [Python-3](https://www.python.org/downloads/) | 
| Flask         | [Flask Homepage](http://flask.pocoo.org/)      | 
| Docker        | [Docker Homepage](https://docs.docker.com/install/)      | 
| Tensorflow    | [Tensorflow Homepage](https://www.tensorflow.org/)      | 
| Keras         | [Keras Homepage](https://keras.io/)                     |
| Tensorflow Serving        |[Tensorflow Serving](https://www.tensorflow.org/tfx/guide/serving)      | 

### Frontend Software Requirements ###

| Software      |  Link         | 
| ------------- |:-------------:| 
| Node.js | [Node Homepage](https://nodejs.org/en/) | 
| Chrome Web Browser  | [Chrome homepage](https://www.google.com/chrome/) | 


### Feed Forward POST JSON ###

```json
curl -i -H "Content-Type: application/json" -X POST -d 
'{"nn_type":"feedforward", 
  "hidden_list":"5 5 1", 
  "inp": "5", 
  "activation_list":"relu relu sigmoid", 
  "optimiser":"adam", 
  "split_value": "0.2", 
  "loss_function": "binary_crossentropy", 
  "data_location":"data/data_new.csv" 
  }' 'http://localhost:3333/api/neural-network/v1.0/'
  ```
  
  ### CNN POST JSON ###
 
```json
curl -i -H "Content-Type: application/json" -X POST -d 
'{"hidden_list":"64 32 4", 
  "inp": "21",
  "kernel_size":"3 3", 
  "activation_list":"relu relu softmax", 
  "epochs":"3", 
  "optimiser":"adam", 
  "split_value": "0.2", 
  "loss_function": "categorical_crossentropy", 
  "data_location":"data/mnist21x21_3789_converted.pklz"}' 'http://localhost:3333/api/neural-network/v1.0/'
```

  ### RNN POST JSON ###
  
  ```json
curl -i -H "Content-Type: application/json" -X POST -d 
'{"nn_type":"rnn", 
  "lstm_out":"256",
  "dense_out":"100",
  "reg_dropout":"0.2",
  "epochs":"10",
  "batch_size":"1000",
  "optimiser":"adam", 
  "split_value": "0.2", 
  "loss_function": "categorical_crossentropy", 
  "data_location":"data/test_data.txt"}' 'http://localhost:3333/api/neural-network/v1.0/'
```
  
### Contributors
| Team Member      |  Github Link| 
| ------------- |:-------------:| 
| Rahul Chowdhury  | [Here](https://github.com/rc1208)      | 
| Ganesh Chandra Satish  | [Here](https://github.com/ganeshchandras)      | 
|  Si Shen       | [Here](https://github.com/shensimeteor)                     |
| Chu Sheng | [Here](https://github.com/bamboo983) | 
| Hansol Yoon       | [Here](https://github.com/hansolyoon)      | 

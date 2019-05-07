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

### 5. How to run (with shell scripts)
1. Open a terminal: `./initial.sh`
2. Start backend: `./backend.sh`
3. Open a new terminal and start frontend: `./frontend.sh`
4. Open a browser and go to: `http://0.0.0.0:3333/`

### 6. How to run (w/o shell scripts)
1. Initialize the SQlite database: `python init_database.py`
2. Install all dependencies
 - `sudo pip install -U Flask`
 - `sudo apt-get install python3`
 - `pip install pandas`
 - `sudo pip install keras`
 - `sudo pip install tensorflow`
 - `sudo pip install scikit-learn`
 - `sudo pip install -U flask-cors`
 - `cd playground` & `sudo npm i` & `sudo npm run build` & `cd ..`

3. Run the Flask Backend Server
 - To start the server: `python3 app.py`
 - Optional Step: If you want to CURL on the models, run: `python request.py` (Comment out the request that you don't want to test)

4. Run the Node Frontend Server
 - Open a new terminal and go to playground: `cd playground`
 - To start the frontend server: `npm run serve`

5. Use some example data for uploading/running test:
 - tabular data: data/data_new.csv (for classification)
 - image data: data/mnist21x21_3789_one_hot.pklz (for image classification)
 - text data: data/asyoulikeit.txt (for language modeling)

6. Open a browser and go to: `http://0.0.0.0:3333/`

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
'{"nn_type":"cnn", \
  "hidden_list":"64 32 4", \
  "width": "21",
  "height":"21",
  "kernel_size":"3 3", \
  "activation_list":"relu relu softmax", \
  "epochs":"3", \
  "optimiser":"adam", \
  "split_value": "0.2", \
  "loss_function": "categorical_crossentropy", \
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
  "data_location":"data/cnn-test.txt"}' 'http://localhost:3333/api/neural-network/v1.0/'
```
  
### Contributors
| Team Member      |  Github Link| 
| ------------- |:-------------:| 
| Rahul Chowdhury  | [Here](https://github.com/rc1208)      | 
| Chu-Sheng Ku | [Here](https://github.com/bamboo983) | 
| Ganesh Chandra Satish  | [Here](https://github.com/ganeshchandras)      | 
|  Si Shen       | [Here](https://github.com/shensimeteor)                     |
| Hansol Yoon       | [Here](https://github.com/hansolyoon)      | 

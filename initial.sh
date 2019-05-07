#!/bin/sh
python init_database.py
sudo pip install -U Flask
sudo apt-get install python3
pip install pandas
sudo pip install keras
sudo pip install tensorflow
sudo pip install scikit-learn
sudo pip install -U flask-cors
cd playground
sudo npm i
sudo npm build
cd ..
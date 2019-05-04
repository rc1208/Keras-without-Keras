#!/usr/bin/env python
import numpy as np
import gzip
import pickle

with gzip.open("data/mnist21x21_3789_one_hot.pklz") as f:
    data = pickle.load(f)
    X1,y1,X2,y2 = data
    n_X1, tmp = X1.shape
    n_X2, tmp = X2.shape
    images = np.zeros((n_X1+n_X2, 21, 21), np.float)
    images[0:n_X1, :, :] = X1.reshape(n_X1, 21, 21)
    images[n_X1:, :, :] = X2.reshape(n_X2, 21, 21)

    labels = np.zeros((n_X1+n_X2, 1), np.float)
    labels[0:n_X1,0] = np.argmax(y1,axis=1)
    labels[n_X1:, 0] = np.argmax(y2,axis=1)

    with gzip.open("data/mnist21x21_3789_converted.pklz","wb") as g:
        pickle.dump((images,labels), g, 1)


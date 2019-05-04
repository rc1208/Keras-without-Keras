#!/usr/bin/env python
import pickle
import gzip
import numpy as np
from PIL import Image


# for image preprocessing
# convert the pngs & csv into a pickle gz file (only gray channel)
# return (n_image, width_image, height_iamge)
def image_pngs_csv_to_pklz(pngfiles, csvfile, output_pklz_file):
    is1st = True
    for png in pngfiles:
        im = Image.open(png).convert('L')
        if(is1st):
            tempa = np.array(im)
            x = tempa.shape
            print(x)


## don't use it, just for 21*21 assignment7 data conversion 
def image_pklz_to_pngs_csv(pklz_file, output_pngdir, output_csvfile):
    pkl_data = pickle.load(gzip.open(pklz_file, "rb"))
    n_image, size_image = pkl_data[0].shape
    

    

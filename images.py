#!/usr/bin/env python
import pickle
import gzip
import numpy as np
from PIL import Image


# for image preprocessing
# convert the pngs & csv into a pickle gz file (only gray channel)
# return (n_image, width_image, height_iamge, n_label)
def image_pngs_csv_to_pklz(pngfiles, csvfile, output_pklz_file):
    is1st = True
    n_image = len(pngfiles)
    for i,png in enumerate(pngfiles):
        im = Image.open(png).convert('L')
        if(is1st):
            tempa = np.array(im)
            w,h = tempa.shape
            dataX = np.zeros((n_image, w, h))
            dataX[0,:,:] = tempa
        else:
            dataX[i,:,:] = np.array(im)
    with open(csvfile, 'r') as f:
        lines = f.readlines()
        label_map = dict([]) #filename -> label (str)
        label_index = dict([]) #label (str) -> index of label (int)
        cnt_label = 0
        for line in lines:
            filename,label = line.strip().split(',')
            if(label in label_index):
                labelidx = label_index[label]
            else:
                label_index[label] = cnt_label
                cnt_label += 1
            label_map[filename] = label
    datay = np.zeros((n_image,1), np.int)
    for i,png in enumerate(pngfiles):
        png_name = png.split('/')[-1]
        datay[i,0] = label_index[label_map[png_name]]
    #summarize dataX, datay
    data = [dataX, datay]
    with gzip.open(output_pklz_file, "wb") as f:
        pickle.dump(data, f, 1)
    return (n_image, w, h, cnt_label)
    
            

## don't use it, just for 21*21 assignment7 data conversion 
def image_pklz_to_pngs_csv(pklz_file, output_pngdir, output_csvfile):
    pkl_data = pickle.load(gzip.open(pklz_file, "rb"))
    n_image, h, w = pkl_data[0].shape
    labels = []
    for i_image in range(n_image):
        rgb = pkl_data[0][i_image,:,:] 
        L_image = Image.fromarray( (pkl_data[0][i_image,:,:] * 256).astype(np.uint8), 'L')
        RGB_image = L_image.convert("RGB")
        im = RGB_image
        im.save("test/mnist_%0.5d.png" % i_image)
        label = pkl_data[1][i_image,0]
        labels.append( "%s,%d\n" %("mnist_%0.5d.png" %i_image, label))
    with open("test/labels.csv", "w") as f:
        for label in labels:
            f.write(label)


def test_image():
    png = "TestCases/p288_corrcoeff_x400_zoomin.png"
    im = Image.open(png).convert('L')
    ary = np.array(im)
    im2 = Image.fromarray(ary)
    print(np.array(im2).shape)
    print(np.array(im2))

#test_image()
#image_pklz_to_pngs_csv("data/mnist21x21_3789_converted.pklz", "temp", "temp")

    

    

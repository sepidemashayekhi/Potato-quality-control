# -*- coding: utf-8 -*-
"""VGG 16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SsE8yDNxZ8Zr_QKOcMidWbxXwNdWIBdL
"""

import tensorflow as tf 
from tensorflow import keras
from keras.layers import Conv2D,Flatten,MaxPool2D,AveragePooling2D,Dense,BatchNormalization
from keras.models import Model

"""# creat model 

"""

def inception_module(x,filters1_1,filters3_3_reduce,filters3_3,filters5_5_reduce,
                     filter5_5,filters_pool_proj,name=None):
  conv1x1=keras.layers.Conv2D(filters1_1,(1,1),padding='same',activation='relu')(x)
  per_conv3x3=keras.layers.Conv2D(filters3_3_reduce,(1,1),padding='same',activation='relu')(x)
  conv3x3=keras.layers.Conv2D(filters3_3,(3,3),padding='same',activation='relu')(per_conv3x3)
  per_conv5x5=keras.layers.Conv2D(filters5_5_reduce,(1,1),padding='same',activation='relu')(x)
  conv5x5=keras.layers.Conv2D(filter5_5,(5,5),padding='same',activation='relu')(per_conv5x5)
  pool_proj=keras.layers.MaxPool2D((3,3),strides=(1,1),padding='same')(x)
  pool_proj=keras.layers.Conv2D(filters_pool_proj,(1,1),padding='same',activation='relu')(pool_proj)
  
  output=keras.layers.concatenate([conv1x1,conv3x3,conv5x5,pool_proj],axis=3,name=name)

  return output

input_layer=keras.layers.Input(shape=(225,225,3))
x=Conv2D(64,(7,7),padding='same',activation='relu')(input_layer)
x=MaxPool2D((3,3))(x)
x=BatchNormalization()(x)
x=Conv2D(64,(1,1),padding='same',activation='relu')(x)
x=Conv2D(192,(3,3),padding='same',activation='relu')(x)
x=BatchNormalization()(x)
x=MaxPool2D((3,3))(x)

x=inception_module(x,64,96,128,16,32,32)
x=MaxPool2D((3,3))(x)
x=inception_module(x,128,128,192,32,96,64)
x=MaxPool2D((3,3))(x)
x=inception_module(x,128,128,192,32,96,64)

x=Flatten()(x)
x=Dense(128,activation='relu')(x)
x=Dense(64,activation='relu')(x)
x=Dense(32,activation='relu')(x)
output=Dense(1,activation='sigmoid')(x)

model=Model(input_layer,output)

model.compile(
          loss      = tf.keras.losses.binary_crossentropy,
          metrics   = tf.keras.metrics.BinaryAccuracy(),
          optimizer = tf.keras.optimizers.Adam())

"""# load data"""

import os 
import numpy as np 
import matplotlib.pyplot as plt 
from keras.preprocessing.image import load_img,img_to_array
from keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split

trainData_path=os.path.join('/content/drive/MyDrive/data2','Train')
testData_path=os.path.join('/content/drive/MyDrive/data2','Test')

data=[]
labels=[]
label=0
for dir in os.listdir(trainData_path):
  for img in os.listdir(os.path.join(trainData_path,dir)):
    imagePath=os.path.join(trainData_path,dir,img)
    image=load_img(imagePath,target_size=(225,225,3))
    image=img_to_array(image)
    data.append(image)
    labels.append(label)
  label+=1

test=[]
labels_test=[]
label=0
for dir in os.listdir(testData_path):
  for img in os.listdir(os.path.join(testData_path,dir)):
    imagePath=os.path.join(testData_path,dir,img)
    image=load_img(imagePath,target_size=(225,225,3))
    image=img_to_array(image)
    test.append(image)
    labels_test.append(label)
  label+=1

data=np.array(data,dtype='float32')
labels=np.array(labels)

test=np.array(test,dtype='float32')
labels_test=np.array(labels_test)

datagen = ImageDataGenerator(rotation_range=20,zoom_range=0.15,
                             width_shift_range=0.2,
                             height_shift_range=0.2,
                             shear_range=0.15,
                             horizontal_flip=True,
                             fill_mode="nearest")

trainGenerator=datagen.flow(data, labels, batch_size=32)

validationGenetator=datagen.flow(test,labels_test,batch_size=32)

"""# fit model """

model.fit_generator(trainGenerator,steps_per_epoch=25,
                       validation_data=validationGenetator,validation_steps=50,epochs=10)

model.save('my_model.h5')
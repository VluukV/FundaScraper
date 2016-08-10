# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 14:56:31 2016

@author: Luuk
"""


import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import normalize
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


csv1 = 'C:\Users\Luuk\Stock prices\Stadsdeel\preprocessed.csv'
house_data = pd.read_csv(csv1)
house_data = house_data.dropna()

features = list(house_data.columns.values)[2:-1]
print features
output = 'Vraagprijs'


def splitData(df, trainPerc=0.6, cvPerc=0.2, testPerc=0.2):
    """
    return: training, cv, test
            (as pandas dataframes)
    params:
              df: pandas dataframe
       trainPerc: float | percentage of data for trainin set (default=0.6
          cvPerc: float | percentage of data for cross validation set (default=0.2)
        testPerc: float | percentage of data for test set (default=0.2)
                  (trainPerc + cvPerc + testPerc must equal 1.0)
    """
    assert trainPerc + cvPerc + testPerc == 1.0

    # create random list of indices
    from random import shuffle
    N = len(df)
    l = range(N)
    shuffle(l)

    # get splitting indicies
    trainLen = int(N*trainPerc)
    cvLen    = int(N*cvPerc)
    testLen  = int(N*testPerc)

    # get training, cv, and test sets
    training = df.ix[l[:trainLen]]
    valid       = df.ix[l[trainLen:trainLen+cvLen]]
    test     = df.ix[l[trainLen+cvLen:]]

    #print len(cl), len(training), len(cv), len(test)

    return training, valid, test

def get_numpy_data(data_sframe, features, output):
    # add the column 'constant' to the front of the features list so that we can extract it along with the others:
    # select the columns of data_SFrame given by the features list into the SFrame features_sframe (now including constant):
    features_sframe = data_sframe[features]
    # the following line will convert the features_SFrame into a numpy matrix:
    feature_matrix = features_sframe.as_matrix()
    # assign the column of data_sframe associated with the output to the SArray output_sarray
    output_sarray = data_sframe[output]
    # the following will convert the SArray into a numpy array by first converting it to a list
    output_array = output_sarray.as_matrix()
    return feature_matrix, output_array
     
def normalize_features(np_array):
    norms = np.linalg.norm(np_array, axis=0)
    features = np_array / norms
    return features, norms

def eucl_dis(vector1,vector2):
    return np.sqrt(((vector1-vector2)**2).sum())

def distance_q_train(features,feature_vector):
    diff = features - feature_vector
    distances = np.sqrt(np.sum(diff**2, axis=1))
    return distances

def k_NN(k,features_train,feature_vector):
    sort_dist = np.argsort(distance_q_train(features_train,feature_vector))
    return sort_dist[:k]

def k_NN_average(k,features_train,output,feature_vector):
    sort_dist = np.argsort(distance_q_train(features_train,feature_vector))
    pred_value = output_train[sort_dist[:k]].sum() # this line takes a vector as input (sort_dis[:k] is a vector), nice
    return pred_value/k

def k_NN_average_array(k,features_train,output,query_matrix):
    pred_array = np.zeros(shape=0)
    for query in query_matrix:
        sort_dist = np.argsort(distance_q_train(features_train,query))
        pred_value = output_train[sort_dist[:k]].sum() # this line takes a vector as input (sort_dis[:k] is a vector), nice
        pred_array = np.append(pred_array,pred_value/k)
    
    return pred_array


train,valid,test = splitData(house_data, trainPerc=0.9, cvPerc=0.05, testPerc=0.05)

train,valid,test = train.dropna(),valid.dropna(),test.dropna()

train = train[features+[output]]
valid = valid[features+[output]]
test = test[features+[output]]


features_train, output_train = get_numpy_data(train, features, output) # Train must include output data
features_valid, output_valid = get_numpy_data(valid, features, output)
features_test, output_test = get_numpy_data(test, features, output)


features_train, norms = normalize_features(features_train) # normalize training set features (columns)
features_test = features_test / norms # normalize test set by training set norms
features_valid = features_valid / norms # normalize validation set by training set norms

feature_vector = features_test[2]
nearest_k = k_NN(10,features_train,feature_vector)
output_1 = output_train[nearest_k[0]]
nearest_k_average = k_NN_average(7,features_train,output_train,feature_vector)

plt.plot(features_test[:,4],output_test,'k.',
        features_test[:,4],k_NN_average_array(7,features_train,output_train,features_test),'r.')

import matplotlib.pyplot as plt

pred_values = k_NN_average_array(3,features_train,output_train,features_test)
RSS = ((output_test-pred_values)**2).sum()
#print RSS
#print ((output_test-np.mean(output_test))**2).sum()
print 'R2 (R Squared):',1-(RSS/((output_test-np.mean(output_test))**2).sum()) # R2 (R Squared) 

""" Test for what k for NN the model is opti
mal
rss_all = []
for k in range(1,16):
    pred_values = k_NN_average_array(k,features_train,output_train,features_valid)
    RSS = ((output_valid-pred_values)**2).sum()
    rss_all.append(RSS)
    print RSS,k
"""
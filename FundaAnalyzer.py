# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 12:13:50 2016

@author: luuk
"""
import pandas as pd
import re
csv1 = "data2016-08-10-amsterdam.csv" # output from scraper
csv2 = "postcode_dist_to_city_center.csv" # output from postcode to city center distance
house_data = pd.read_csv(csv1)
postcode_dist_data = pd.read_csv(csv2)


def postcode_to_dist(string):
    result = string.split(' ')
    try:
        postcode = result[0]+result[1]
    except:
        postcode = 'NaN'
    if postcode != 'NaN':
        try:
                
            distance = (postcode_dist_data.loc[postcode_dist_data['postcode'] == postcode]).iloc[0]['distance']
            return distance
        except:
            print 'Did not work'
            return 'NaN'
    else:
        return 'NaN'    

def string_to_number(string):
    text = str(string)
    output = re.findall(r'[1-9](?:\d{0,2})(?:,\d{3})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0', text)
    if output:
        return output[0]
    else:
        return None

def string_to_m2backy(string):
    text = str(string)
    text = text.replace(",", ".")
    output = re.findall(r'\d+(?:.\d+)?', text) 
    print output
    #output = re.findall(r'[1-9](?:\d{0,2})(?:,\d{3})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0', text)
    try:
        if len(output)==3:
            #print float(output[0])
            return float(output[0])
        elif len(output)==2:
            #print float(output[0])*float(output[1])
            return float(output[0])*float(output[1])
        else:
            return 0
    except:
        return 0
 
        

def get_dist():
    house_data['Distance to center'] = house_data['Postcode'].apply(postcode_to_dist)

def get_string_to_number(feature):
    house_data[feature] = house_data[feature].apply(string_to_number)

def get_m2backy():
    house_data['Achtertuin'] = house_data['Achtertuin'].apply(string_to_m2backy)


get_dist()
get_m2backy()
features = ['Aantal woonlagen','Aantal kamers','Aantal badkamers','Periodieke bijdrage','Woonoppervlakte']

for feature in features:
    get_string_to_number(feature)

processed_data = house_data['Vraagprijs']
processed_data = processed_data.to_frame()


features_2 = ['Distance to center','Achtertuin','Externe bergruimte']
for feature in features_2:
    features.append(feature)

for feature in features:
    processed_data[feature] = house_data[feature]

print len(features)
processed_data['Externe bergruimte'] = processed_data['Externe bergruimte'].fillna(value=0)
processed_data['Aantal badkamers'] = processed_data['Aantal badkamers'].fillna(value=1)
processed_data['Periodieke bijdrage'] = processed_data['Periodieke bijdrage'].fillna(value=0)
processed_data['Aantal woonlagen'] = processed_data['Aantal woonlagen'].fillna(value=1)

processed_data['tag'] = house_data['Link']
print processed_data


processed_data.to_csv('preprocessed.csv')


  
        
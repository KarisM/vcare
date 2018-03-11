# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 22:47:48 2018

@author: Kariza
"""

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import datetime
from sklearn.cluster import KMeans
import sys
import pymysql
import json
import math
from scipy.fftpack import fft, fftfreq
import statsmodels.api as sm

df = pd.read_csv('Sensor_data2.csv',index_col = 0,names = ['dateTime','carId','sensorId','sensorName','value'])
df = df[0:]
df_position = pd.read_csv('Time_data2.csv',index_col = 0,names = ['dateTime','carId','DTC','latitude','longtitude','distance'])
df_position = df_position[0:]

def toDateTime(array):
    for index in array:
        index[0] = datetime.datetime.strptime(index[0],"%Y-%m-%d %H:%M:%S")
    
def toFloat(array):
    for index in array:
        index[1] = float(index[1])

df_load = df[df.sensorId == 4].loc[:,['dateTime','value']].values
df_temp = df[df.sensorId == 5].loc[:,['dateTime','value']].values
df_rpm = df[df.sensorId == 12].loc[:,['dateTime','value']].values
df_speed = df[df.sensorId == 13].loc[:,['dateTime','value']].values
df_fuel = df[df.sensorId == 47].loc[:,['dateTime','value']].values
df_distance = df[df.sensorId == 49].loc[:,['dateTime','value']].values
df_voltage = df[df.sensorId == 66].loc[:,['dateTime','value']].values
df_fuelair = df[df.sensorId == 68].loc[:,['dateTime','value']].values

df_position = df_position.values



#Transform to datetime type
toDateTime(df_load)
toDateTime(df_temp)
toDateTime(df_rpm)
toDateTime(df_speed)
toDateTime(df_fuel)
toDateTime(df_distance)
toDateTime(df_voltage)
toDateTime(df_fuelair)
toDateTime(df_position)

#Transform value to float
toFloat(df_load)
toFloat(df_temp)
toFloat(df_rpm)
toFloat(df_speed)
toFloat(df_fuel)
toFloat(df_distance)
toFloat(df_voltage)
toFloat(df_fuelair)

def cleanData(array):
    for idx in range(len(array)):
        if idx != 0 and idx != len(array) - 1: 
            if array[idx,1] == 0:
                array[idx,1] = (array[idx-1,1] + array[idx+1,1])/2
        if idx == 0:
            if array[idx,1] == 0:
                array[idx,1] = array[idx+1,1]
        if idx == len(array) - 1 :
            if array[idx,1] == 0:
                array[idx,1] = array[idx-1,1]
                
def smoothingLowess(array):
    x = list(range(len(array[:,1])))
    lowess_result = sm.nonparametric.lowess(array[:,1], x, frac=2/.3, return_sorted=False)
    result = []
    for i in range(len(array)):    
        result.append([array[i,0],lowess_result[i]])
    return np.array(result)

def cleanPosition(position):
    lat = position[:,3]
    long = position[:,4]
    
    #clean lat
    for idx in range(len(lat)):
        if lat[0] == 0:
            for j in range(len(lat)):
                if lat[j] != 0:
                    lat[idx] = lat[j] 
                    break 
             
        elif lat[idx] == 0:
           for j in range(len(lat[idx:len(lat)])):
                if lat[j] != 0:
                    kepp_buffer = lat[j] 
                    break 
           lat[idx] = (lat[idx-1]+kepp_buffer)/2
           
           
    #clean long
    for idx in range(len(long)):
        if long[0] == 0:
            for j in range(len(long)):
                if long[j] != 0:
                    long[idx] = long[j] 
                    break 
             
        elif long[idx] == 0:
           for j in range(len(long[idx:len(long)])):
                if long[j] != 0:
                    kepp_buffer = long[j] 
                    break 
           long[idx] = (long[idx-1]+kepp_buffer)/2
           
#        print(idx+1,lat[idx],long[idx])
           
cleanPosition(df_position)                
            

#Transform value to float
cleanData(df_load)
cleanData(df_temp)
cleanData(df_rpm)
cleanData(df_speed)
cleanData(df_fuel)
cleanData(df_distance)
cleanData(df_voltage)
cleanData(df_fuelair)

df_load = smoothingLowess(df_load)
df_temp = smoothingLowess(df_temp)
df_rpm = smoothingLowess(df_rpm)
df_speed = smoothingLowess(df_speed)
df_fuel = smoothingLowess(df_fuel)
df_distance = smoothingLowess(df_distance)
#df_voltage = smoothingLowess(df_voltage)
df_fuelair = smoothingLowess(df_fuelair)


"""
--------------------------------------------------------------Sampling Data-----------------------------------------------------------------------
"""
def fuelPercentToData(array):
    for idx in range(len(array)):
        array[idx,1] = (array[idx,1]/100.00) * 40.00
    return array
df_fuel = fuelPercentToData(df_fuel)
    
#def sampling_data(array):
#    data_list = []
#    for idx in range(0,60*16,60): # 16 data to summerize to 15
#        idx = len(array) - idx - 1
#        avg = np.mean(array[idx-59:idx+1,1])
#        data_list.append(avg)
#    print(data_list)
#    return data_list.reverse()

def fuelUsage(distance,fuel,position):
    buffer_result = []
    result = []
    if len(distance) == len(fuel):
        for idx in range(1,len(distance)):
            buffer_result.append([distance[idx,0],(distance[idx,1]-distance[idx-1,1])/(fuel[idx-1,1]-fuel[idx,1]),position[idx,3],position[idx,4]])
        buffer_result = np.array(buffer_result)
    for idx in range(0,len(buffer_result)-6,6):
        result.append([buffer_result[idx+5,0],np.mean(buffer_result[idx:idx+5,1]),buffer_result[idx+5,2],buffer_result[idx+5,3]])
    result = np.array(result)
#    print(result)
    return result
fuelConsumption = fuelUsage(df_distance,df_fuel,df_position)
#fuelConsumption = smoothingLowess(fuelConsumption)
        
"""
--------------------------------------------------------------Plot data-----------------------------------------------------------------------
"""
def plot_data(array,name):
    fig = plt.figure(figsize=(8, 6), dpi=80)
    ax = plt.subplot(111)
    ax.set_title(name)
    ax.plot(array[:,0],array[:,1])
    ax.legend()
#    fig.savefig(name + '_smoothplot.png')

#plot_data(df_load,'load')
#plot_data(df_temp,'temp')
#plot_data(df_rpm,'rpm')
#plot_data(df_speed,'speed')
#plot_data(df_fuel,'fuel')
#plot_data(df_distance,'distance')
#plot_data(df_voltage,'voltage')
#plot_data(df_fuelair,'fuelair')

plot_data(fuelConsumption,"fuelConsumption")

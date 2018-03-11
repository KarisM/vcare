# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 14:27:47 2018

@author: Kariza
"""
"""
-------------------------------Load Data-------------------------------
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

#Transform date-time to time
def deleteDate(array):
    for index in array:
        index[0] = index[0].split(" ")[1]
        #print(index[0])

def toDateTime(array):
    for index in array:
        index[0] = datetime.datetime.strptime(index[0],"%Y-%m-%d %H:%M:%S")
    
def toFloat(array):
    for index in array:
        index[1] = float(index[1])
    

#For creating kmeans model
def anomalyModel(array,n_cluster):
    kmeans = KMeans(n_clusters=n_cluster, random_state=0).fit(array[:,1].reshape(-1,1))
    
    
    for iter_ in range(n_cluster): 
        for data in range(len(kmeans.labels_)):
            if kmeans.labels_[data] == iter_:
#                print("Labels:",kmeans.labels_[data],"index:",data,"Value:",array[data])
                break
    
    #Count each label
    label_count = []
    for iter_ in range(n_cluster): 
        count = 0
        for data in kmeans.labels_:
            if data == iter_:
                count += 1
        label_count.append(count)
#    print("****label_count:",label_count)
    
    #Find anomaly label
    label_anomaly = -1
    min_count = 1000000
    for index in range(len(label_count)):
        if min_count > label_count[index]:
            min_count = label_count[index]
            label_anomaly = index
     
    
    #Find min,max value of anomaly
    max_of_anomaly = -1
    min_of_anomaly = 1000000
    for data in range(len(kmeans.labels_)):
        if kmeans.labels_[data] == label_anomaly:
            if max_of_anomaly < array[data][1]:
                max_of_anomaly = array[data][1]
            elif min_of_anomaly > array[data][1]:
                min_of_anomaly = array[data][1] 
#    print("****label_anomaly:",label_anomaly,"Min:",min_of_anomaly,"Max:",max_of_anomaly)
                
    error = math.sqrt(kmeans.inertia_/label_count[0])
    return [kmeans,label_anomaly,error,min_of_anomaly,max_of_anomaly]




"""
----------------------------------------------------------Anomaly Detection-------------------------------------------------------------------
"""

"""
#For detecting anomaly
def anomalyDetection(detect_list,kmeans):
    anomaly_label = kmeans[1]
    n_clusters = kmeans[0].n_clusters
#    print("\n")
#    print("------------------------------- Detection --------------------------------")
    predict_results = kmeans[0].predict([[detect_list[1]]])
    if predict_results == anomaly_label:
#        print("Status Anomaly!!")
#        print("Anomally:",detect_list,"Predict Label:",predict_results)
        return 1
    else:
#        print("Status Normal")
#        print("Data:",detect_list,"Predict Label:",predict_results)
        return 0
#    print("--------------------------------------------------------------------------")
"""

def generalAnomalyDetection(detect_list,kmeans,type_sensor):
    n_clusters = kmeans[0].n_clusters
    anomaly_label = kmeans[1]
    error = kmeans[2]
    min_value = kmeans[3]
    max_value = kmeans[4]
#    print("\n")
#    print("------------------------------- Detection --------------------------------")
    if detect_list[1] > (max_value + error) or detect_list[1] < (min_value - error):
#        print("Status Anomaly!!")
#        print("Anomally:",detect_list)
        return "Status Anomaly " + type_sensor
    else:
#        print("Status Normal")
#        print("Data:",detect_list)
        return "Status Normal"
#    print("--------------------------------------------------------------------------")


def anomalyDetectionVolt(detect_list):
#    print("\n")
#    print("------------------------------- Detect Volt ------------------------------")
    if detect_list[1] < 10 or detect_list[1] > 20:
#        print("Status Anomaly Voltage!!")
#        print("Data:",detect_list)
        return "Status Anomaly Voltage"
    else:
#        print("Status Normal")
#        print("Data:",detect_list)
        return "Status Normal"
#    print("--------------------------------------------------------------------------")
    
def anomalyDetectionSpeed(detect_list):
#    print("\n")
#    print("------------------------------- Detect Speed ------------------------------")
    if detect_list[1] > 180:
#        print("Status High Speeds!!")
#        print("Data:",detect_list)
        return "Status High Speed"
    else:
#        print("Status Normal")
#        print("Data:",detect_list)
        return "Status Normal"
#    print("--------------------------------------------------------------------------")
    
def anomalyDetectionFuel(detect_list):
#    print("\n")
#    print("------------------------------- Detect Fuel ------------------------------")
    if detect_list[1] < 15:
#        print("Status Low Fuel!!")
#        print("Data:",detect_list)
        return "Status Low Fuel"
    else:
#        print("Status Normal")
#        print("Data:",detect_list)
        return "Status Normal"
#    print("--------------------------------------------------------------------------")
    
def anomalyDetectionDistance(detect_list):
#    print("\n")
#    print("------------------------------- Detect Distance ------------------------------")
    if detect_list[1] % 10000 == 9800:
#        print("Status Alert Distance!!")
#        print("Data:",detect_list)
        return "Status Alert Distance"
    else:
#        print("Status Normal")
#        print("Data:",detect_list)
        return "Status Normal"
#    print("--------------------------------------------------------------------------")


#Get latest data for each sensor
def queryLastData(sensorId):
    carId = 1
     #connect to mysql
    conn = pymysql.connect(host='localhost', 
                        port=3306, 
                        user='VCare_dev', 
                        passwd='!12qwaszx?', 
                        db='VCareDB')
    cur = conn.cursor()
    #get data mileage from database
    sql = "SELECT time, value value FROM carSensor WHERE carId = " + str(carId) + " AND sensorId = " + str(sensorId) + " ORDER BY id DESC LIMIT 1"
    cur.execute(sql)
    #convert object to data
    result = []
    for row in cur:
        result = row
    
    result = list(result)
    result[1] = float(result[1])
    conn.commit()
    cur.close()
    conn.close()
    return result
    

def main():
    carId = sys.argv[1]
    # print("carId",carId)
    n_cluster = 8
    #print("PYTHON CODE")
    #read Data
    columns=['id', 'dateTime', 'carId', 'sensorId', 'sensorName', 'value']
    #df = pd.read_csv("Sensor_data.csv", skiprows=1, header = None, names = columns)
    df = pd.read_csv("./Sensor_data.csv", skiprows=1, header = None, names = columns)
    
    #Delete duplicate id
    df.__delitem__('id')
    #if(df.isnull().values.any()):
    #    print("----------Found Missing----------")
    df_load = df[df.sensorId == 4].loc[:,['dateTime','value']].values
    df_temp = df[df.sensorId == 5].loc[:,['dateTime','value']].values
    df_rpm = df[df.sensorId == 12].loc[:,['dateTime','value']].values
    df_speed = df[df.sensorId == 13].loc[:,['dateTime','value']].values
    df_fuel = df[df.sensorId == 47].loc[:,['dateTime','value']].values
    df_distance = df[df.sensorId == 49].loc[:,['dateTime','value']].values
    df_voltage = df[df.sensorId == 66].loc[:,['dateTime','value']].values
    
    """
    ---------------------------------------------------------------Preprocessing-------------------------------------------------------------------
    """
    
    #Transform to datetime type
    toDateTime(df_load)
    toDateTime(df_temp)
    toDateTime(df_rpm)
    toDateTime(df_speed)
    toDateTime(df_fuel)
    toDateTime(df_distance)
    toDateTime(df_voltage)
    
    #Transform value to float
    toFloat(df_load)
    toFloat(df_temp)
    toFloat(df_rpm)
    toFloat(df_speed)
    toFloat(df_fuel)
    toFloat(df_distance)
    toFloat(df_voltage)
    #Detect Anomaly 
    #print("-------------------------------------Load-----------------------------------")
    kmean_load = anomalyModel(df_load,n_cluster) 
    #print("-------------------------------------Temp-----------------------------------")
    kmean_temp = anomalyModel(df_temp,n_cluster) 
    #print("-------------------------------------RPM-----------------------------------")
    kmean_rpm = anomalyModel(df_rpm,n_cluster) 
    
    #kmean_voltage = anomalyModel(df_voltage,n_cluster) 
    #kmean_speed = anomalyModel(df_speed)
    #kmean_fuel = anomalyModel(df_fuel)
    #kmean_distance = anomalyModel(df_distance)
    status_load = generalAnomalyDetection(queryLastData(4),kmean_load,"Load") #(detect_list,kmeans)
    status_temp = generalAnomalyDetection(queryLastData(5),kmean_temp,"Temperature") #(detect_list,kmeans)
    status_rpm = generalAnomalyDetection(queryLastData(12),kmean_rpm,"RPM") #(detect_list,kmeans)
    status_volt = anomalyDetectionVolt(queryLastData(66)) #(detect_list)
    status_speed = anomalyDetectionSpeed(queryLastData(13)) #(detect_list)
    status_fuel = anomalyDetectionFuel(queryLastData(47)) #(detect_list)
    status_distance = anomalyDetectionDistance(queryLastData(49)) #(detect_list)
    
    #Send out data
    data_out = '{"status":200, "error":null, "response":[{"load":'+ str(status_load) + '},{"temp":'+ str(status_temp) + '},{"rpm":'+ str(status_rpm) + '},{"volt":'+ str(status_volt) + '},{"speed":'+ str(status_speed) + '},{"fuel":'+ str(status_fuel) + '},{"distance":' + str(status_distance) + '}]}'
    data_out = json.dumps(json.loads(data_out))
    print(data_out)
    
    sys.stdout.flush()
    
 # Start process
if __name__ == '__main__':
    main()
   
    
    

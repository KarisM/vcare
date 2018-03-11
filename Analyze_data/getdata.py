
import numpy as np
import pandas as pd
import pymysql.cursors
import datetime

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='VCare_dev',
                             password='!12qwaszx?',
                             db='VCareDB',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
data = []
#with connection.cursor() as cursor:
#        # Create a new record
##        sql = "SELECT * FROM carSensor cs JOIN sensor s ON cs.sensorId = s.sensorId WHERE DATE(`time`) = CURDATE()"
#        sql = "SELECT * FROM carSensor cs JOIN sensor s ON cs.sensorId = s.sensorId WHERE DATE(`time`) = '2018-03-05'"
#        cursor.execute(sql)
#        for row in cursor:
#            #print(row['carId'])
#            data.append([row['time'].strftime("%Y-%m-%d %H:%M:%S"),row['carId'],row['sensorId'],str(row['sensorName']),str(row['value'])])
#connection.close()
#
#print(data)
#
#
#data = pd.DataFrame(data)
#data.to_csv("Sensor_data2.csv", sep=',')

data = []
with connection.cursor() as cursor:
        # Create a new record
#        sql = "SELECT * FROM carSensor cs JOIN sensor s ON cs.sensorId = s.sensorId WHERE DATE(`time`) = CURDATE()"
        sql = "SELECT * FROM carGPS cg WHERE DATE(`time`) = '2018-03-05'"
        cursor.execute(sql)
        for row in cursor:
            #print(row['carId'])
            data.append([row['time'].strftime("%Y-%m-%d %H:%M:%S"),row['carId'],row['DTC'],row['latitude'],row['longtitude'],row['distance']])
connection.close()

print(data)


data = pd.DataFrame(data)
data.to_csv("Time_data2.csv", sep=',')


#!/usr/bin/python3

import requests
import subprocess
"""
args = ("/home/pi/clowPI/dht11")
popen = subprocess.Popen(args, stdout=subprocess.PIPE)
popen.wait()
output = popen.stdout.read()
if popen.returncode == 0:
    print(output)
else:
    print("call failed")
"""
import sys
import Adafruit_DHT

humidity, temperatureC = Adafruit_DHT.read_retry(11, 4)
tempF = (temperatureC*9/5.0) + 32
print('tc:{},tf:{},h:{}'.format(temperatureC,tempF,humidity))
#print('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity))
r = requests.get("http://10.0.1.21:80/tempHumidIn/'{}'/{}/{}".format('dht11',tempF,humidity))

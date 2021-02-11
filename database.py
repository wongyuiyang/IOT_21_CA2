#Python imports
import sys
import random
import datetime
from time import sleep
import threading
import pickle
import json

#Web and Server imports
import telepot
import mysql.connector
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()

#Sensor imports
import Adafruit_DHT
from gpiozero import LED
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from gpiozero import MCP3008

from flask import Flask, request, Response, render_template

#AWS imports
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

GPIO.setwarnings(False)

#Pickle to communicate between server.py and database.py
filename = 'flags'

#LED
led = LED(17)
#Temperature and Humidity Sensor
DHT_pin = 4
#Set Water Level Sensor pin as input
GPIO.setup(18, GPIO.IN)
#Set Relay as output
GPIO.setup(23, GPIO.OUT)
GPIO.setwarnings(False)
#Light Sensor
adc = MCP3008(channel=0)

#Database
try:
    #AWS functions - Connect device to AWS
    #Custom MQTT message callback
    def customCallback(client, userdata, message):
        print("--------------")
        print("Received a new message: ")
        print(message.payload)
        print("From topic: ")
        print(message.topic)
        print("--------------")
    
    host = "a3st2xvjc2igm0-ats.iot.us-east-1.amazonaws.com"
    rootCAPath = "rootca.pem"
    certificatePath = "certificate.pem.crt"
    privateKeyPath = "private.pem.key"

    my_rpi = AWSIoTMQTTClient("PubSub-p1827976") #Endpoint
    my_rpi.configureEndpoint(host, 8883) #Standard port number for MQTT - 8883,...
    my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
    my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
    my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

    #Connect and subscribe to AWS IoT
    my_rpi.connect()
    my_rpi.subscribe("sensors/#", 1, customCallback)
    print("Connected to AWS!")
    sleep(2)

    #Set a main update flag to break all loops and threads
    update = True

    #Water pump flag to check for empty bottle
    bottle_flag = 0

    #Telepot
    #Telegram bot token
    my_bot_token = '1415384651:AAFnfPFrEF5e_pAL42U-YHKh6Ij10gASGW0'
    bot = telepot.Bot(my_bot_token)

    while update:
        try:
            #Check pickled file
            f = open(filename, 'rb')
            flags_dict = pickle.load(f)
            f.close()

            #DHT Process
            #Dummy values
            #dummy_temperature = random.randint(20,40)
            #dummy_humidity = random.randint(20,90)
            #DHT values
            humidity, temperature = Adafruit_DHT.read_retry(11, DHT_pin)
            #Fix humidity >100% error
            if humidity > 100:
                humidity -= 120
            #Print
            print('Temp:{:.1f}C'.format(temperature))
            print('Humidity:{:.1f}%'.format(humidity))
            #AWS - Publish DHT values to DynamoDB table DHT
            message = {}
            message["deviceid"] = "deviceid_wongyuiyang"
            DHT_datetime_now = datetime.datetime.now()
            message["datetimeid"] = DHT_datetime_now.strftime("%Y-%m-%d %H:%M:%S")
            print(DHT_datetime_now.isoformat())
            message["humidity"] = humidity
            message["temperature"] = temperature
            my_rpi.publish("sensors/DHT", json.dumps(message), 1)
            sleep(1)
            
            #LED Process
            #Get local time in 24 hour format
            datetime_now = datetime.datetime.now()
            datetime_hour = int(datetime_now.strftime("%H"))
            #Publish light levels to the sensors/light topic
            #my_rpi.publish("sensors/light", str(adc.value), 1)
            #LED turns on if 'sunlight' low (> 0.2)
            if flags_dict['ledFlag'] == 1: #LED Light Sensor
                if adc.value > 0.2:
                    led.on()
                    print("LED Light Sensor - Low Light Levels, LED on")
                else:
                    led.off()
                    print("LED Light Sensor - High Light Levels, LED off")
            elif flags_dict['ledFlag'] == 2: #LED Datetime
                if datetime_hour >= 11 and datetime_hour < 18: #LED turns on from 11AM-6PM
                    led.on()
                    print("LED Datetime - on from 11AM-6PM")
                else:
                    led.off()
                    print("LED Datetime - off from 6PM-11AM")
            else:
                print("LED offline")
                led.off()
            sleep(1)

            #Water Pump Process
            if flags_dict['pumpFlag'] == 1: #Auto-watering on
                if GPIO.input(18): #Water Level Sensor == True, water level sensed
                    bottle_flag = 0
                    print("Water level high!")
                    GPIO.output(23, GPIO.HIGH)
                elif bottle_flag != 2:
                    bottle_flag += 1
                    print("Water level low!")
                    GPIO.output(23, GPIO.LOW)
                    #Pump water for two seconds before turning off
                    sleep(4)
                    GPIO.output(23, GPIO.HIGH)
                else:
                    #update flags_dict to turn off water pump
                    flags_dict['pumpFlag'] = 2
                    f = open(filename, 'wb')
                    pickle.dump(flags_dict, f)
                    f.close()
                    print("Pump bottle out of water! Please refill! Smart-Pump shutting down.")
                    bot.sendMessage(1395047909, 'Refill Smart-Pump bottle!')
            else:
                print("Water pump offline")
                GPIO.output(23, GPIO.HIGH)
            sleep(1)

        except KeyboardInterrupt:
            update = False
            cursor.close()
            cnx.close()
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
except:
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])

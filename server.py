#Python imports
import sys
import threading
import json
import numpy
import datetime
import decimal
from time import sleep
import pickle
import os

#Sensor imports
from gpiozero import LED
from gpiozero import MCP3008
from picamera import PiCamera
import Adafruit_DHT

#Web and Server imports
from flask import Flask, render_template, jsonify, request,Response
import mysql.connector
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import telepot

#AWS imports
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3
from boto3.dynamodb.conditions import Key, Attr
import botocore
#Create an S3 resource
s3 = boto3.resource('s3')
#Set the bucket name
bucket = 'sp-p1827976-s3-bucket'
exists = True
try:
    s3.meta.client.head_bucket(Bucket=bucket)
except botocore.exceptions.ClientError as e:
    error_code = int(e.response['Error']['Code'])
    if error_code == 404:
        exists = False
if exists == False:
  s3.create_bucket(Bucket=bucket,CreateBucketConfiguration={'LocationConstraint': 'us-east-1'})
#Set dynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

gevent.monkey.patch_all()

class GenericEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj) 
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:  
            return json.JSONEncoder.default(self, obj) 

def data_to_json(data):
    json_data = json.dumps(data,cls=GenericEncoder)
    return json_data        

app = Flask(__name__)

#Pickle
#Flags by default set all functions to offline
flags_dict = {'ledFlag': 3, 'pumpFlag': 2}
filename = 'flags'
f = open(filename, 'wb')
pickle.dump(flags_dict, f)
f.close()

#Set User Session
session = {'loggedin':False, 'username':'placeholder'}

@app.route("/")
def chartsimple():
    if session['loggedin'] == False:
        return render_template('login.html')
    return render_template('index.html', value = session['username'])

@app.route("/login", methods=['GET', 'POST'])
def login():
    #reset session
    global session
    session['loggedin'] = False
    #Begin login
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        #Connect with DynamoDB
        #Get entire list of users
        table = dynamodb.Table('Users')
        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang'),
            ScanIndexForward=False
        )
        items = response['Items']
        #Check if account exist
        for i in items:
            if i['name'] == username and i['password'] == password:
                #Create session data
                session['loggedin'] = True
                session['username'] = username
                print("Current session is as user "+session['username'])
                # Redirect to home page
                return 'Logged in successfully! Returning to home page in 5 seconds... <meta http-equiv="refresh" content="5; url = /"/>'
        #Else display 'Incorrect' and return to login.html
        return 'Incorrect username/password! Returning to login page in 5 seconds... <meta http-equiv="refresh" content="5; url = /login"/>'
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = False
        account2 = False
        
        #Connect with DynamoDB
        #Get entire list of users
        table = dynamodb.Table('Users')
        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang'),
            ScanIndexForward=False
        )
        items = response['Items']
        for i in items:
            if i['name'] == username:
                account = True
            if i['email'] == email:
                account2 = True
        #Does account username already exist?
        if account == True:
            return 'Username taken, please choose another username! Returning to register page in 5 seconds... <meta http-equiv="refresh" content="5; url = /register"/>'
        #Does email already exist?
        elif account2 == True:
            return 'Email already registered, please choose another email! Returning to register page in 5 seconds... <meta http-equiv="refresh" content="5; url = /register"/>'
        else:
            #Add new account
            table.put_item(Item={'deviceid':'deviceid_wongyuiyang', 'name':username, 'email':email, 'password':password})
            return 'New account added! Returning to login page in 5 seconds... <meta http-equiv="refresh" content="5; url = /login"/>'
    return render_template('register.html')

#DHT function
pin = 4

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            #Connect with DynamoDB
            table = dynamodb.Table('DHT')
            now = datetime.datetime.now()
            startdate = now.strftime("%Y-%m")
            response = table.query(
                KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang') & Key('datetimeid').begins_with(startdate),
                ScanIndexForward=False
            )
            items = response['Items']
            n=10 # limit to last 10 items
            db_data = items[:n]
            data_reversed = db_data[::-1]
            data = {'chart_data': data_to_json(data_reversed), 'title': "IOT Data"}
            #print(data)
            return jsonify(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

@app.route("/getCurrentDHT",methods = ['POST', 'GET'])
def getCurrentDHT():
    humidity, temperature = Adafruit_DHT.read_retry(11, pin)
    #Fix humidity >100% error
    if humidity > 100:
        humidity -= 120
    data = {'temperature': temperature, 'humidity': humidity}
    return jsonify(data)


@app.route("/getHighestDHT", methods = ['POST', 'GET'])
def getHighestDHT():
    if request.method == 'POST':
        try:
            #Connect with DynamoDB
            table = dynamodb.Table('DHT')
            now = datetime.datetime.now()
            startdate = now.strftime("%Y-%m-%d")
            #Get all values for today
            response = table.query(
                KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang') & Key('datetimeid').begins_with(startdate),
                ScanIndexForward=False
            )
            items = response['Items']
            humidity = 0
            temperature = 0
            #Get highest values
            for i in items:
                if i['humidity'] >= humidity:
                    humidity = i['humidity']
                if i['temperature'] >= temperature:
                    temperature = i['temperature']
            data = {'temperature': int(temperature), 'humidity': int(humidity)}
            #print(data)
            return jsonify(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

#LED function
def ledOne():
    global flags_dict
    flags_dict['ledFlag'] = 1
    f = open(filename, 'wb')
    pickle.dump(flags_dict, f)
    f.close()
    return "LED using Light Sensor"

def ledTwo():
    global flags_dict
    flags_dict['ledFlag'] = 2
    f = open(filename, 'wb')
    pickle.dump(flags_dict, f)
    f.close()
    return "LED on between 11AM-6PM"

def ledThree():
    global flags_dict
    flags_dict['ledFlag'] = 3
    f = open(filename, 'wb')
    pickle.dump(flags_dict, f)
    f.close()
    return "LED Off"

@app.route("/writeLED/<status>")
def writeLED(status):
    if status == 'One':
        response = ledOne()
    elif status == 'Two':
        response = ledTwo()
    else:
        response = ledThree()
    return response

#WaterPump Function
def pumpOn():
    global flags_dict
    flags_dict['pumpFlag'] = 1
    f = open(filename, 'wb')
    pickle.dump(flags_dict, f)
    f.close()
    return "On"

def pumpOff():
    global flags_dict
    flags_dict['pumpFlag'] = 2
    f = open(filename, 'wb')
    pickle.dump(flags_dict, f)
    f.close()
    return "Off"

@app.route("/writePump/<status>")
def writePump(status):
    if status == 'On':
        response = pumpOn()
    else:
        response = pumpOff()
    return response

#By default, assume TV and Fan are off when server.py is run. 0 is off, 1 is on
TVFlag = 0
FanFlag = 0

#Infrared Transmitter - TV Function
def TVPower():
    global TVFlag
    global TVOn_datetime
    global TVOff_datetime
    global TVDiffH
    if TVFlag == 0:
        #Turn on the TV
        os.system('irsend SEND_ONCE remote TV_BTN_POWER')
        #Record time when TV is turned on
        TVOn_datetime = datetime.datetime.now()
        TVFlag = 1
        return "TV Power On"
    elif TVFlag == 1:
        #Turn off the TV
        os.system('irsend SEND_ONCE remote TV_BTN_POWER')
        #Record time when TV is turned off
        TVOff_datetime = datetime.datetime.now()
        #Get how long TV has been on for
        TVDiff = TVOff_datetime - TVOn_datetime
        #Calculate how many hours TV was on
        TVDiffH = TVDiff.total_seconds() / 3600
        #Format into 3 decimal points
        TVDiffHf = round(TVDiffH,3)
        print("TV was on for "+str(TVDiffHf)+" hours!")
        TVMonitor(TVDiffHf)
        TVFlag = 0
        return "TV Power Off"

def TVMonitor(hours):
    try:
        #Connect with DynamoDB
        table = dynamodb.Table('IRUsage')
        now = datetime.datetime.now()
        startdate = now.strftime("%Y-%m-%d")
        #Get IRUsage for today
        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang') & Key('datetimeid').eq(startdate),
            ScanIndexForward=False
        )
        items = response['Items']
        
        #Check if items list is empty
        if not items:
            #Add TVHours
            table.put_item(Item={'deviceid':'deviceid_wongyuiyang', 'datetimeid':startdate, 'TVHours':str(hours), 'FanHours':str(0)})
            print(str(startdate)+" record added to database!")
        #Else, append new hours
        else:
            #Update TVHours
            table.update_item(
                Key={'deviceid':'deviceid_wongyuiyang', 'datetimeid':startdate},
                UpdateExpression="set TVHours=:r",
                ExpressionAttributeValues={
                ':r':str(float(items[0]['TVHours']) + hours)
            })
            print(str(startdate)+" record updated!")
    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

@app.route("/writeTV/Power")
def writeTV():
    response = TVPower()
    return response

#Infrared Transmitter - Fan Function
def FanPower():
    global FanFlag
    global FanOn_datetime
    global FanOff_datetime
    global FanDiffH
    if FanFlag == 0:
        #Turn on the fan
        os.system('irsend SEND_ONCE remote FAN_BTN_POWER')
        #Record time when fan is turned on
        FanOn_datetime = datetime.datetime.now()
        FanFlag = 1
        return "Fan Power On"
    elif FanFlag == 1:
        #Turn off the fan
        os.system('irsend SEND_ONCE remote Fan_BTN_POWER')
        #Record time when fan is turned off
        FanOff_datetime = datetime.datetime.now()
        #Get how long fan has been on for
        FanDiff = FanOff_datetime - FanOn_datetime
        #Calculate how many hours TV was on
        FanDiffH = FanDiff.total_seconds() / 3600
        #Format into 3 decimal points
        FanDiffHf = round(FanDiffH,3)
        print("Fan was on for "+str(FanDiffHf)+" hours!")
        FanMonitor(FanDiffHf)
        FanFlag = 0
        return "FAN Power Off"

def FanMonitor(hours):
    try:
        #Connect with DynamoDB
        table = dynamodb.Table('IRUsage')
        now = datetime.datetime.now()
        startdate = now.strftime("%Y-%m-%d")
        #Get IRUsage for today
        response = table.query(
            KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang') & Key('datetimeid').eq(startdate),
            ScanIndexForward=False
        )
        items = response['Items']
        
        #Check if list is empty
        if not items:
            #Add FanHours
            table.put_item(Item={'deviceid':'deviceid_wongyuiyang', 'datetimeid':startdate, 'TVHours':str(0), 'FanHours':str(hours)})
            print(str(startdate)+" record added to database!")
        #Else, append new hours
        else:
            #Update FanHours
            table.update_item(
                Key={'deviceid':'deviceid_wongyuiyang', 'datetimeid':startdate},
                UpdateExpression="set FanHours=:r",
                ExpressionAttributeValues={
                ':r':str(float(items[0]['FanHours']) + hours)
            })
            print(str(startdate)+" record updated!")
    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

@app.route("/writeFan/Power")
def writeFan():
    response = FanPower()
    return response

#Display TV and Fan usage on index.html
@app.route("/api/getIRdata",methods = ['POST', 'GET'])
def apidata_getIRdata():
    if request.method == 'POST':
        try:
            #Connect with DynamoDB
            table = dynamodb.Table('IRUsage')
            now = datetime.datetime.now()
            startdate = now.strftime("%Y-%m")
            response = table.query(
                KeyConditionExpression=Key('deviceid').eq('deviceid_wongyuiyang') & Key('datetimeid').begins_with(startdate),
                ScanIndexForward=False
            )
            items = response['Items']
            #Change str values to float
            for i in items:
                i['FanHours'] = float(i['FanHours'])
                i['TVHours'] = float(i['TVHours'])
            
            n=10 # limit to last 10 items
            db_data = items[:n]
            data_reversed = db_data[::-1]
            data = {'chart_data': data_to_json(data_reversed), 'title': "IRUsage Data"}
            return jsonify(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

#AWS Picam Function
camera = PiCamera()

#Rekognition
def detect_labels(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
	return response['Labels']

def detect_faces(bucket, key, max_labels=10, min_confidence=90, region="us-east-1"):
	rekognition = boto3.client("rekognition", region)
	response = rekognition.detect_faces(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		Attributes=['ALL']
	)
	return response['FaceDetails']

def CaptureImage():
    global bucket
    highestconfidence = 0
    datetime_now = datetime.datetime.now()
    capture_name = "image{}.jpg".format(datetime_now.strftime("%Y-%m-%d_%H:%M:%S"))
    #Capture image and name it the current datetime, temporarily store it
    camera.capture('/home/pi/Desktop/'+capture_name)
    #Upload image to AWS s3 bucket
    s3.Object(bucket, capture_name).put(Body=open('/home/pi/Desktop/'+capture_name, 'rb'))
    #AWS rekognition for objects
    obj_rek_str = 'Object Recognition Results:<br>'
    #Check if there are any results in detect_labels
    if detect_labels(bucket, capture_name):
        for label in detect_labels(bucket, capture_name):
            obj_rek_str += "{Name} - {Confidence}%<br>".format(**label)
            if label["Confidence"] >= highestconfidence:
                highestconfidence = label["Confidence"]
                best_bet_item = label["Name"]     
        
        #Round highestconfidence into 3 decimal points
        highestconfidence = round(highestconfidence,3)
        obj_rek_str += "This should be a {} with confidence {}%".format(best_bet_item, highestconfidence)
    else:
        obj_rek_str += 'No objects detected.'
    #AWS rekognition for faces
    face_rek_str = 'Face Recognition Results:<br>'
    #Check if there are any results in detect_faces
    if detect_faces(bucket, capture_name):
        for faceDetail in detect_faces(bucket, capture_name):
            #Get age range
            ageLow = faceDetail['AgeRange']['Low']
            ageHigh = faceDetail['AgeRange']['High']
            face_rek_str += 'Age between {} and {} years old<br>'.format(ageLow, ageHigh)
            face_rek_str += 'Here are the other attributes:<br>'
            emotion_confidence = 0
            emotion_type = ''
            
            #Get the emotion with highest confidence
            for i in faceDetail['Emotions']:
                if i['Confidence'] >= emotion_confidence:
                    emotion_confidence = i['Confidence']
                    emotion_type = i['Type']
            #Round emotion_confidence to 3 decimal points
            emotion_confidence = round(emotion_confidence,3)
            face_rek_str += 'Emotion should be {} with confidence {}%<br>'.format(emotion_type, emotion_confidence)
            
            #Get the gender
            gender_value = faceDetail['Gender']['Value']
            gender_confidence = faceDetail['Gender']['Confidence']
            #Round gender_confidence to 3 decimal points
            gender_confidence = round(gender_confidence,3)
            face_rek_str += 'Gender should be {} with confidence {}%'.format(gender_value, gender_confidence)
    else:
        face_rek_str += 'No faces detected.'
    #Delete image from raspberry pi
    os.remove('/home/pi/Desktop/'+capture_name)
    #Prepare camera_dict for html
    camera_dict = {'image': "https://sp-p1827976-s3-bucket.s3.amazonaws.com/"+capture_name, 'message': "Image captured to https://sp-p1827976-s3-bucket.s3.amazonaws.com/"+capture_name, 'message2': obj_rek_str, 'message3': face_rek_str}
    return jsonify(camera_dict)

@app.route("/writeCamera/<status>")
def writeCamera(status):
    if status == 'Capture':
        response = CaptureImage()
    return response

#Telegram bot token
my_bot_token = '1415384651:AAFnfPFrEF5e_pAL42U-YHKh6Ij10gASGW0'
bot = telepot.Bot(my_bot_token)

#Telegram bot functions
def respondToMsg(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print(chat_id)
    print('Got Telegram command: {}'.format(command))

    if command == 'LEDOne':
        bot.sendMessage(chat_id, ledOne())
    elif command == 'LEDTwo':
        bot.sendMessage(chat_id, ledTwo())
    elif command == 'LEDThree':
        bot.sendMessage(chat_id, ledThree())
    elif command == 'TVPower':
        bot.sendMessage(chat_id, TVPower())
    elif command == 'FanPower':
        bot.sendMessage(chat_id, FanPower())

bot.message_loop(respondToMsg)
print('Listening for RPi commands...')

#Main
if __name__ == '__main__':
    try:
        print('Server waiting for requests')
        http_server = WSGIServer(('0.0.0.0', 8001), app)
        app.debug = True
        http_server.serve_forever()
    except:
        print("Exception")
        #Release Picamera resources
        camera.close()
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
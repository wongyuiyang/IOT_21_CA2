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

def connect_to_mysql(host,user,password,database):
    try:
        cnx = mysql.connector.connect(host=host,user=user,password=password,database=database)
        cursor = cnx.cursor()
        print("Successfully connected to database!")
        return cnx,cursor
    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None

def fetch_fromdb_as_json(cnx,cursor,sql):
    try:
        cursor.execute(sql)
        row_headers=[x[0] for x in cursor.description] 
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(dict(zip(row_headers,result)))

        data_reversed = data[::-1]
        data = {'data':data_reversed}
        return data_to_json(data)
    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None
                            

app = Flask(__name__)

session = {'loggedin':False, 'id':0, 'username':'placeholder'}

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
        sql="SELECT * FROM users WHERE name = %s AND password = %s"
        cnx = mysql.connector.connect(host='localhost',user='assignmentuser',password='admin',database='assignmentdatabase')
        cursor = cnx.cursor()
        cursor.execute(sql, (username, password))
        account = cursor.fetchone()
        #Check if account exist
        if account:
            #Create session data
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            print("Current session is as user "+session['username'])
            # Redirect to home page
            return 'Logged in successfully! Returning to home page in 5 seconds... <meta http-equiv="refresh" content="5; url = /"/>'
        else:
            return 'Incorrect username/password! Returning to login page in 5 seconds... <meta http-equiv="refresh" content="5; url = /login"/>'
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        sql="SELECT * FROM users WHERE name = '"+str(username)+"'"
        sql2="SELECT * FROM users WHERE email = '"+str(email)+"'"
        cnx = mysql.connector.connect(host='localhost',user='assignmentuser',password='admin',database='assignmentdatabase')
        cursor = cnx.cursor()
        cursor.execute(sql)
        account = cursor.fetchone()
        cursor.execute(sql2)
        account2 = cursor.fetchone()
        #Does account username already exist?
        if account:
            return 'Username taken, please choose another username! Returning to register page in 5 seconds... <meta http-equiv="refresh" content="5; url = /register"/>'
        #Does email already exist?
        elif account2:
            return 'Email already registered, please choose another email! Returning to register page in 5 seconds... <meta http-equiv="refresh" content="5; url = /register"/>'
        else:
            #Add new account
            sql = "INSERT INTO users VALUES (NULL, %s, %s, %s)"
            cursor.execute(sql, (username, password, email))
            cnx.commit()
            return 'New account added! Returning to login page in 5 seconds... <meta http-equiv="refresh" content="5; url = /login"/>'
    return render_template('register.html')

#Pickle
#Flags by default set all functions to offline
flags_dict = {'ledFlag': 3, 'pumpFlag': 2}
filename = 'flags'
f = open(filename, 'wb')
pickle.dump(flags_dict, f)
f.close()

#DHT function
pin = 4

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            host='localhost'; user='assignmentuser'; password='admin'; database='assignmentdatabase'
            sql="SELECT * FROM DHT ORDER BY datetimeinfo DESC LIMIT 10"
            cnx,cursor = connect_to_mysql(host,user,password,database)
            json_data = fetch_fromdb_as_json(cnx,cursor,sql)
            loaded_r = json.loads(json_data)
            data = {'chart_data': loaded_r, 'title': "IOT Data"}
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
            #Get current date in YYYY-MM-DD format
            datetime_now = datetime.datetime.now()
            datetime_YMD = datetime_now.strftime("%Y-%m-%d")
            #Match datetime_YMD with YYYY-MM-DD% stored in datetimeinfo
            sql="SELECT MAX(temperature) as temperature, MAX(humidity) as humidity FROM DHT WHERE datetimeinfo LIKE '"+datetime_YMD+"%'"
            cnx = mysql.connector.connect(host='localhost',user='assignmentuser',password='admin',database='assignmentdatabase')
            cursor = cnx.cursor()
            cursor.execute(sql) 
            results = cursor.fetchone()
            #print(results)
            temperature = int(results[0])
            humidity = int(results[1])
            data = {'temperature': temperature, 'humidity': humidity}
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
    current_date = datetime.date.today()
    try:
        #Check current date
        sql="SELECT * FROM IRUsage WHERE dateinfo LIKE '"+str(current_date)+"'"
        cnx = mysql.connector.connect(host='localhost',user='assignmentuser',password='admin',database='assignmentdatabase')
        cursor = cnx.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        #Check if list is empty
        if not results:
            sql = "INSERT INTO IRUsage (dateinfo, TVHours) VALUES (%(v1)s, %(v2)s)"
            cursor.execute(sql, {'v1':str(current_date), 'v2':hours})
            cnx.commit()
            print(str(current_date)+" record added to database!")
        #Else, append new hours
        else:
            sql = "UPDATE IRUsage SET TVHours = TVHours+"+str(hours)+" WHERE dateinfo LIKE '"+str(current_date)+"'"
            cursor.execute(sql)
            cnx.commit()
            print("Database for TV record updated!")
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
    current_date = datetime.date.today()
    try:
        #Check current date
        sql="SELECT * FROM IRUsage WHERE dateinfo LIKE '"+str(current_date)+"'"
        cnx = mysql.connector.connect(host='localhost',user='assignmentuser',password='admin',database='assignmentdatabase')
        cursor = cnx.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        #Check if list is empty
        if not results:
            sql = "INSERT INTO IRUsage (dateinfo, FanHours) VALUES (%(v1)s, %(v2)s)"
            cursor.execute(sql, {'v1':str(current_date), 'v2':hours})
            cnx.commit()
            print(str(current_date)+" record added to database!")
        #Else, append new hours
        else:
            sql = "UPDATE IRUsage SET FanHours = FanHours+"+str(hours)+" WHERE dateinfo LIKE '"+str(current_date)+"'"
            cursor.execute(sql)
            cnx.commit()
            print("Database for Fan record updated!")
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
            host='localhost'; user='assignmentuser'; password='admin'; database='assignmentdatabase'
            sql="SELECT * FROM IRUsage ORDER BY dateinfo DESC LIMIT 10"
            cnx,cursor = connect_to_mysql(host,user,password,database)
            json_data = fetch_fromdb_as_json(cnx,cursor,sql)
            loaded_r = json.loads(json_data)
            data = {'chart_data': loaded_r, 'title': "IRUsage Data"}
            return jsonify(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

#Picam Function
camera = PiCamera()

def CaptureImage():
    datetime_now = datetime.datetime.now()
    capture_name = "image{}.jpg".format(datetime_now.strftime("%Y-%m-%d_%H:%M:%S"))
    #Capture image and name it the current datetime
    camera.capture('/home/pi/labs/CA1/static/picam/'+capture_name)
    camera_dict = {'image': "/static/picam/"+capture_name, 'message': "Image captured to /home/pi/labs/CA1/static/picam/"+capture_name}
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
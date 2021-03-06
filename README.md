## ST0324 : INTERNET OF THINGS
## DIPLOMA IN INFOCOMM SECURITY MANAGEMENT (DISM)
# IOT 21 CA2 step-by-step tutorial
Wong Yui Yang and Er Yong Keng Ryan's IOT CA2 github repo.

This link contains the Bootstrap theme for this project's web interface: https://startbootstrap.com/theme/sb-admin-2

To install the Bootstrap theme, create a *static* folder in the same folder where *database.py*, *server.py* and the *templates* folder are stored. In the SBAdmin template, you will see that the CSS, Javascript etc codes are stored in 5 different folders as shown.

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F0.1.jpg?raw=true)

Copy the 5 folders into the *static* folder. You will now be able to use the Bootstrap theme.

# Our Smart-Room App
## Table of contents

# 1 Overview of Our Smart-Room App.
Our application is a Smart-Room application that provides both device automation and monitoring features. It is intended for users who have indoor hydroponic plants that are unable to receive sunlight normally. It is also intended for users who want to monitor their room's environment and device usage.  The application works with Amazon Web Services to store information in their databases as well as use their other services.

Our Smart-Room app has a Smart-Plant feature for hydroponic plants which automates plant watering using a water-level sensor and a water pump. It can also be used to provide indoor light for the plant using a LED with two different settings, light-based and time-based.

The app is attached with a Raspberry Pi camera module that can be used to take a picture of the plant and save it within AWS S3. The app provides image and face recognition for the photos taken using AWS rekognition as an added feature.

Our Smart-Room app uses a DHT sensor to monitor the humidity and temperature of the room. It displays the current humidity and temperature, the highest recorded humidity and temperature for that day, and a graph that shows the real-time changes in humidity and temperature.

Our Smart-Room app can be used to power on and off devices within the room if they receive infrared signals. The Smart-Room app uses an infrared transmitter and infrared receiver to record and send infrared signals to the user's room devices. Through this process, my Smart-Room app can monitor the usage of room devices and display it in a bar graph.

Our Smart-Room app is also compatible with a Telegram bot. The Telegram bot allows the user to manage LED settings and turn their room devices on and off using the infrared transmitter. It will also notify the user if the water pump's bottle is empty and requires refilling.

## 1.1 How the final RPI set-up looks like

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F1.jpg?raw=true)
Figure 1

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F2.jpg?raw=true)
Figure 2

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F3.jpg?raw=true)
Figure 3

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F4.jpg?raw=true)
Figure 4

## 1.2 How the web app looks like

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F5.png?raw=true)
Figure 5

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F6.png?raw=true)
Figure 6

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F7.png?raw=true)
Figure 7

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F8.jpg?raw=true)
Figure 8

## 1.3 Overview of System Architecture

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F9.png?raw=true)
Figure 9

# 2 Hardware Requirements
1.	One DHT sensor
2.	One LED
3.	One Pi Camera Module
4.	One Light-Dependant Resistor (Light Sensor)
5.  One MCP3008 ADC
6.	One Non-contact digital water/liquid level sensor
7.	One Water Pump
8.	One Relay Board
9.	One IR Receiver
10.	One IR Transmitter

You will also require a breadboard, two 10k ohms resistors for the DHT sensor and LDR, and one 330 ohms resistor for the LED.

# 3 Hardware setup
## 3.1 Fritzing Diagram
The hardware should be setup according to the fritzing diagram shown.

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.jpg?raw=true)
Figure 10

## 3.2 Water pump
The raspberry pi will not be able to power to water pump by itself. To solve this issue, a relay board must be set up between the raspberry pi, the water pump and an outside power source.

First, hook up the raspberry pi to the relay board by connecting a male-to-female red wire from the 5V pin on the raspberry pi to the VCC pin on the relay board. Next, connect a male-to-female black wire from the GND pin on the raspberry pi to the GND pin on the relay board. To control the relay, connect a male-to-female blue wire from the GPIO23 pin on the raspberry pi to the IN4 pin on the relay board. (Depending on which relay the user uses, this can be IN1, IN2…)

After hooking up the raspberry pi and the relay board, connect the GND wire of the water pump to the GND wire of the external power source. The relay will have three outputs where wires can be connected to by screwing them in. The middle output is where the positive wire of the external power source is connected to, while the left output is where the positive wire of the water pump is connected to. (See Figure 4 and Figure 10 for reference)

## IR Receiver and IR Transmitter
To set up the IR transmitter to send IR signals, you will need to receive IR signals with the IR receiver and configure some lirc files. First, install the lirc module with 'sudo apt-get install lirc'. After installing lirc, reboot your raspberry pi using 'sudo reboot'. Configure /boot/config.txt and make these changes using 'sudo nano /boot/config.txt':
```
# Uncomment this to enable the lirc-rpi module
#dtoverlay=lirc-rpi
dtoverlay=gpio-ir,gpio_pin=5
dtoverlay=gpio-ir-tx,gpio_pin=6

Next, configure /etc/lirc/hardware.conf:

# /etc/lirc/hardware.conf
#
# Arguments which will be used when launching lircd
LIRCD_ARGS="--device /dev/lirc0"

#Don't start lircmd even if there seems to be a good config file
#START_LIRCMD=false

#Don't start irexec, even if a good config file seems to exist.
#START_IREXEC=false

#Try to load appropriate kernel modules
LOAD_MODULES=true

# Run "lircd --driver=help" for a list of supported drivers.
DRIVER="default"
\# usually /dev/lirc0 is the correct setting for systems using udev
DEVICE="/dev/lirc0"
MODULES=""

# Default configuration files for your hardware if any
LIRCD_CONF=""
LIRCMD_CONF=""
```
Now, you can begin recording the IR signals of remote controls you use for your room devices. Ensure that the lirc module is stopped by using 'sudo systemctl stop lirc'. To begin recording IR signals with the IR receiver, enter 'mode2 -m -d /dev/lirc1' into the command line. Point your remote control at the IR receiver and press a button. You will see the IR signal displayed like so:

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F11.jpg?raw=true)

Copy the block of numbers within the red box, ignoring '…-pulse' and '…-space'. This will be the IR signal to replicate on the IR transmitter. To configure your IR transmitter to send this signal, configure the /etc/lirc/lircd.conf file. In the lircd.conf file, you can configure the name of the 'remote' that is the IR transmitter and the name of buttons assigned to the IR signal. An example of how your lircd.conf file should be configured is as so:
```
begin remote

  name  remote
  bits           16
  flags SPACE_ENC|CONST_LENGTH
  eps            30
  aeps          100

  header        622   505
  one           625  1634
  zero          625   504
  ptrail        627
  repeat       9071  2209
  pre_data_bits   15
  pre_data       0xFF
  gap          108057
  toggle_bit_mask 0x0

      begin raw_codes

          name TV_BTN_POWER
             4561     4635      569      586      548     1767
      570     1744      569     1743      571     1743
      547     1765      549      607      548      608
      548      609      572     1743      546     1765
      573     1740      548     1765      578     1736
      550      606      549      606      577      618
      514      602      573     1741      574     1743
      546      610      570      582      573      581
      575      581      573     1744      569     1742
      572      583      575      582      572     1762
      558     1786      522     1808      483     1764
      569

           name FAN_BTN_POWER

      9043     4448      580      551      603      522
      579      548      579      548      605      522
      608      520      605      522      630     1622
      607     1645      605     1648      604     1648
      605     1648      579     1673      579     1674
      606     1645      581      548      605     1648
      604      523      606      521      581      546
      604      523      604      523      603      525
      602      525      631      496      578     1674
      608     1642      606     1648      603     1649
      605     1646      605     1650      579     1673
      604

      end raw_codes


end remote
```
Once you have configured the lircd.conf file, start the lirc module through' sudo systemctl start lirc'. Position your IR transmitter towards the device you want to control, and use the 'irsend' command to send IR signals from your IR transmitter. For example, 'irsend SEND_ONCE remote TV_BTN_POWER' is a command that sends an IR signal associated with the button TV_BTN_POWER once.

# 4 Software setup
## Software checklist
The following software is needed for the program to work.

Telepot API. For the RPi to be able to communicate with Telegram. You will need to create a bot in Telegram, copy down the bot token, and replace the bot token value in the python files with your own.
```
sudo pip install telepot
```

Lirc module. The LIRC moduel is required for the IR retriever and IR transmitter to work.
```
sudo apt-get install lirc
```
Run 'sudo systemctl start lirc' in command line to allow the IR transmitter to transmit IR signals. To check the status of lirc, run 'sudo systemctl status lirc'.
```
sudo systemctl start lirc
sudo systemctl status lirc
```

AWS Python Library. The AWS Python Libraries are requires before the program can interact with AWS.
```
sudo pip install --upgrade --force-reinstall pip==9.0.3
sudo pip install AWSIoTPythonSDK --upgrade --disable-pip-version-check
sudo pip install --upgrade pip
```

Awscli.
```
sudo pip install awscli
```
If Awscli is already installed, but you want to upgrade it,
```
sudo pip install awscli --upgrade
```

Botocore
```
sudo pip install botocore
```
If botocore is already installed, but you want to upgrade it,
```
sudo pip install botocore --upgrade
sudo pip install boto3 --upgrade
```

Ngrok can be used to host the web app on the internet. Instead of downloading the grok binary from the grok website, you can use Node.js npm package to streamline the installation process.
```
sudo npm install --unsafe-perm -g ngrok
```
Run 'ngrok http 8001' to begin hosting your raspberry pi server on the internet.
```
ngrok http 8001
```

## 4.1 AWS - Creating a "Thing"
a) Search for "IOT Core" and click it to access the IOT Core dashboard.
b) In the left navigation pane, click “Manage” to expand it, then choose “Things”.
c) Choose "Register a thing" or "Create" to create a new Thing.
d) Name your Thing and click "Create a single thing".

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.1.jpg?raw=true)

e) Choose “One-click certificate creation” to generate an X.509 certificate and key pair. Download the certificate, public key and private key. For the root CA, you can download at this link: https://docs.aws.amazon.com/iot/latest/developerguide/server-authentication.html#server-authentication-certs. Right click on Amazon Root CA 1 and click "Save As".

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.2.jpg?raw=true)

f) Store the certificates in the same folder as *server.py* and *database.py*. Rename the certificates to friendlier names as shown. Next, click the “Activate” button. Almost immediately, you should see “Successfully activated certificate” and the Activate button changes to “Deactivate”.

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.3.jpg?raw=true)

g) Click to the next page, and click “Register Thing”.

## 4.2 AWS - Create a Security Policy for your RPi
a) On the left IOT Core dashboard, select Policies under the Secure sub-menu.
b) On the next page, choose “Create new policy”.
c) Key in the following configuration with a policy name of your choosing:

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.4.jpg?raw=true)

d) Click "Create"

## 4.3 AWS - Attach Security Policy and Thing to your Cert
a) On the left IOT Core dashboard, select Certificates under the Secure sub-menu.
b) Click on the certificate. Under Actions, click "Attach Policy" and choose the policy you created earlier. Click the "Attach" button.
c) Under Actions, click "Attach Thing" and select the checkbox next to the Thing you created. Click "Attach".

## 4.4 AWS - REST API Endpoint of your Thing
Click “Manage->Things” and choose your Thing. On the next screen, choose “Interact”. Copy and note down the REST API endpoint, as you will need it to replace the endpoints in the python code.

## 4.5 AWS - Create Role
a) Search for the IAM service on AWS Console and choose “Roles”.
b) Click “Create Role” and on the next page, choose “AWS service”, then “IOT”.
c) Under “Select your use case”, select IoT.
d) Click “Next->Permissions”, click “Next->Tags”, click “Next->Review”.
e) You will see a page that requires you to input a name for your Role. Key in a role name of your choosing e.g **SmartRoomRole**.

## 4.6 AWS - Create DynamoDB tables
Our Smart-Room App uses 3 DynamoDB tables: DHT, IRUsage and Users.

a) Open the Amazon DynamoDB console and click “Create Table”.
b) For table DHT, create the table using the attributes as shown below with default table settings, and click "create":

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.5.jpg?raw=true)

c) For table IRUsage, create the table using the attributes as shown below with default table settings, and click "create":

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.6.jpg?raw=true)

d) For table Users, create the table using the attributes as shown below with default table settings, and click "create":

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.7.jpg?raw=true)

## 4.7 AWS - Create DynamoDB table rule
Our Smart-Room App uses one rule to send DHT data received from a the RPi to the DHT table.

a) In the AWS IoT console, in the left navigation pane, choose “Act”, then “Create a rule”.
b) On the Create a rule page, in the Name field, type a name for your rule e.g **DHT_DynamoDBRule**. In the Description field, type a description for the rule.
c) Scroll down to Rule Query statement. Type *SELECT * FROM 'sensors/DHT'*.
d) In Set one or more actions, choose Add action.
e) On the Select an action page, select the action below.  Next, choose Configure action.

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.8.jpg?raw=true)

f) On the Configure action page, from the SNS target drop-down list, choose the DHT table you created earlier.
g) Under **IAM role name**, choose the one you created (**SmartRoomRole**) from the drop-down list and click “Update Role”.
h) Click “Create” then "Create Rule".

## 4.8 AWS - Create your AWS credentials file
Our Smart-Room App stores pictures taken by the PiCam into an Amazon S3 bucket and uses AWS Rekognition. For this function to work, you will need to create an AWS credentials file in your RPi.

a) On your AWS Account Status, Click “Account Details” button. You will be shown a screen similar to this. Copy the AWS CLI code.

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.9.jpg?raw=true)

b) In your RPI, open a new Terminal window and type:
```
sudo rm ~/.aws/credentials
sudo nano ~/.aws/credentials
```
c) Paste the codes you copied into the editor, and click Ctrl-O, Ctrl-X to save.

## 4.9 Create and configuring a bucket on Amazon S3
To display images on the web app, the Amazon S3 bucket permissions and policy must be configured.

a) In the AWS console, search for S3. Click "Create bucket".
b) Type in a unique name for your bucket and choose a suitable region.
c) Click the "Permissions" tab of your newly created bucket. Click the "Edit" button under **Block public access (bucket settings)**. Uncheck everything like shown, and click "Save changes".

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.10.jpg?raw=true)

e) Click the "Edit" button under **Bucket policy**, and copy this code into **Policy**, with the resource name changed to your bucket. Click "Save changes".

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.11.jpg?raw=true)

# 5 Expected Outcome
To test if the program works, follw this quick-start guide:
1)	First connect hardware as in Figure 1 or Figure 10.
2)	Run 'sudo systemctl start lirc' in command line to allow the IR transmitter to transmit IR signals. To check the status of lirc, run 'sudo systemctl status lirc'.
3)	Run 'ngrok http 8001' to begin hosting your raspberry pi server on the internet.
4)	Edit the ~/.aws/credentials file with your current AWS account credentials.
5)	Ensure that your AWS certificates have been downloaded and are in the same folder as database.py and server.py.
6)	Run the database.py file for hardware and database functions.
```
python database.py
```
7)	Run the server.py file for web server.
```
python server.py
```
8)	View the web server using the link ngrok provided.

The following is the link to the video demonstration of what the application should look like. https://www.youtube.com/watch?v=kCmDNtVrbrw&feature=youtu.be

The **database.py** terminal should show the data being sent to the DynamoDB DHT table, the current LED status, the water level and water pump status. The DynamoDB DHT table should be populated whenever **database.py** displays the MQTT message.

The **server.py** terminal should show the various HTTP GET requests as shown. Due to restrictions of Ngrok, **server.py** is only able to update the data displayed on the web app every minute. This means that graphs such as the DHT graph and IRUsage graph will only update after a minute has passed.

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F10.12.jpg?raw=true)

# 6 References
Turning Raspberry pi into a remote controller: https://devkimchi.com/2020/08/12/turning-raspberry-pi-into-remote-controller/

Using the RPi.GPIO module: https://learn.sparkfun.com/tutorials/raspberry-gpio/python-rpigpio-api

Ngrok guide to host raspberry pi web server on the internet: https://thisdavej.com/how-to-host-a-raspberry-pi-web-server-on-the-internet-with-ngrok/

Dfrobot guide for non-contact liquid level sensor: https://wiki.dfrobot.com/Non-contact_Liquid_Level_Sensor_XKC-Y25-T12V_SKU__SEN0204

Online Manual for LIRC: https://www.lirc.org/html/

Getting started developing with Python and DynamoDB: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.html

Boto3 Docs 1.17.5 documentation for DynamoDB: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html

Configuring Amazon S3 bucket permissions and policy:
https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteAccessPermissionsReqd.html

### -- End of CA2 step-by-step tutorial --

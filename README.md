# RYAN SCRIPT
My name is Ryan, the second member of our group. Now that you know our names, let us introduce you to our project.

Hi, my name is Ryan and I will demonstrate the parts of the app that I coded.
The first feature is monitoring the room's humidity and temperature levels using a DHT sensor. Over here is the DHT sensor. On the web interface, the app will display the current and highest humidity and temperature levels for today. The app will also display a real-time graph using data that is stored in a DynamoDB table called DHT.

The second feature is an LED that can be set to three different states through buttons on the web interface. The first state is a light-based state that is dependant on the LDR. When the LDR records low light levels, the LED will turn on. When light levels are high, the LED will turn off. Using a flash light to simulate high-levels, you can see that the LED turns off. The second state is a time-based state. As shown on the web interface, the LED will turn on between 11AM-6PM to simulate a natural day-night cycle. Since it is currently 4PM at the making of the video, the LED is turned on. The third state is having the LED completely turned off.

The third feature is capturing an image and performing object and facial recognition using the Pi Camera module. To capture an image, the user first clicks on the 'Capture Image' button on the web interface. Let's take a picture of the camera-man, my groupmate Yui Yang. This process may take a few minutes. After the Picam takes a picture, the app shows that the image has been stored in an Amazon S3 bucket with the following name. Looking into the Amazon S3 bucket shows that the image is there. The image is then processed through Amazon Rekognition before the results are displayed onto the web interface. As you can see, Rekognition correctly detected that there was a camera in the photo, and that my group mate is a male with calm facial features.

One intermediate bonus feature I coded is displaying images from the AWS S3 bucket. Normally, images within an AWS S3 bucket cannot be displayed unless they are publicly available and the user has a key to view them. As shown in the video, the permissions of the bucket has been set to public. However, this is not enough. To access the image without a key, the bucket's policy must be configured like this. This allows the web interface to display the captured image using this link, which is the link of the latest image captured.

## ST0324 : INTERNET OF THINGS
## DIPLOMA IN INFOCOMM SECURITY MANAGEMENT (DISM)
# IOT 21 CA2 step-by-step tutorial
Wong Yui Yang and Er Yong Keng Ryan's IOT CA2 github repo.

This google drive link contains the bootstrap theme for this project's web interface: https://drive.google.com/drive/folders/1dTitfVtMkjH2HaNa2ziMBlF1izzy7apA?usp=sharing

Place the *static* folder in the same folder where *database.py*, *server.py* and the *templates* folder are stored.

# Our Smart-Room App
## Table of contents

# 1 Overview of Our Smart-Room App.
Our application is a Smart-Room application that provides both device automation and monitoring features. It is intended for users who have indoor hydroponic plants that are unable to receive sunlight normally. It is also intended for users who want to monitor their room's environment and device usage.  The application works with Amazon Web Services to store information in their databases as well as use their other services.

Our Smart-Room app has a Smart-Plant feature for hydroponic plants which automates plant watering using a water-level sensor and a water pump. It can also be used to provide indoor light for the plant using a LED with two different settings, light-based and time-based.

The app is attached with a Raspberry Pi camera module that can be used to take a picture of the plant and save it within AWS S3. The app provides image and face recognition for the photos taken using AWS rekognition as an added feature.

Our Smart-Room app uses a DHT sensor to monitor the humidity and temperature of the room. It displays the current humidity and temperature, the highest recorded humidity and temperature for that day, and a graph that shows the real-time changes in humidity and temperature.

Our Smart-Room app can be used to power on and off devices within the room if they receive infrared signals. The Smart-Room app uses an infrared transmitter and infrared receiver to record and send infrared signals to the user's room devices. Through this process, my Smart-Room app can monitor the usage of room devices and display it in a bar graph.

Our Smart-Room app is also compatible with a Telegram bot. The Telegram bot allows the user to manage LED settings and turn their room devices on and off using the infrared transmitter. It will also notify the user if the water pump's bottle is empty and requires refilling.

## How the final RPI Set-up looks like

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F1.jpg?raw=true)
Figure 1

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F2.jpg?raw=true)
Figure 2

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F3.jpg?raw=true)
Figure 3

![alt text](https://github.com/wongyuiyang/IOT_21_CA2/blob/main/images/F4.jpg?raw=true)
Figure 4

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

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

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
c) Key in the following configuration:

| Field | Description |
| --- | --- |
| git status | List all new or modified files |
| git diff | Show file differences that haven't been staged |

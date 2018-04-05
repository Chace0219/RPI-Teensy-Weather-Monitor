
### Logging function package in order to display AWS Connection and callback messages
import sys
import logging

### Time package, used to implement thread and timing in RPI
import time

### JSON Processing Python package
import json

### URL Processing Package, used to download images from URL provided in JSON via MQTT for user photos 
import urllib
import urllib2
import datetime

from PyCRC.CRC32 import CRC32

'''
Install from pip
pip install AWSIoTPythonSDK

Download and Build from source in Git Hub

git clone https://github.com/aws/aws-iot-device-sdk-python.git
cd aws-iot-device-sdk-python
sudo python setup.py install
'''
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient ## AWS IOt MQTT Client Library 

### SPI and GPIO package for Raspberry PI Python
'''
sudo apt-get update
sudo apt-get install build-essential python-pip python-dev python-smbus git
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo python setup.py install
'''
import Adafruit_GPIO.SPI as SPI

#SSD1351 driver port from original adafruit driver using Python. It is based on the SPI interface.
'''
git clone https://github.com/twchad/Adafruit_Python_SSD1351.git
cd Adafruit_Python_SSD1351
sudo python setup.py install
'''
import Adafruit_SSD1351

# Image Library used for photos on screen
import Image


'''
	tar -xzf crc16-0.1.1.tar.gz
	cd crc16-0.1.1
	python setup.py build
	sudo python setup.py install
'''
import crc16

# this is for UART for Raspberry Pi
import serial # Referenced from https://pypi.python.org/pypi/pyserial/2.7 

import threading, time

from json import load
from urllib2 import urlopen

'''
	Function for getting public ip of current RPI
'''
def GetPublicIPAddr():
	my_ip = load(urlopen('http://jsonip.com'))['ip']
	return my_ip

WunderAPIKey = "973c64631b35d69e"

def GetWeatherInfo():
	APIRequest = "http://api.wunderground.com/api/"
	APIRequest += WunderAPIKey
	APIRequest += "/geolookup/conditions/astronomy/q/autoip.json?geo_ip="
	APIRequest += GetPublicIPAddr()
	
	print APIRequest

	f = urllib2.urlopen(APIRequest)
	json_string = f.read()
	parsed_json = json.loads(json_string)
	location = parsed_json['location']['city']
	temp_c = parsed_json['current_observation']['temp_c']
	weather_des = parsed_json['current_observation']['weather']
	precip_today_metric = parsed_json['current_observation']['precip_today_metric']
	print "precip_today_metric %s" % (precip_today_metric)
	print "Current temperature in %s is: %s celcius degree and %s." % (location, temp_c, weather_des)
	
	currtime = parsed_json['moon_phase']['current_time']['hour'] + ":"
	currtime += parsed_json['moon_phase']['current_time']['minute']
	currtime += ":00"
	print "Current time %s" % (currtime)
	
	sunrise = parsed_json['moon_phase']['sunrise']['hour'] + ":"
	sunrise += parsed_json['moon_phase']['sunrise']['minute']
	sunrise += ":00"
	print "sunrise time %s" % (sunrise)

	sunset = parsed_json['moon_phase']['sunset']['hour'] + ":"
	sunset += parsed_json['moon_phase']['sunset']['minute']
	sunset += ":00"
	print "sunset time %s" % (sunset)

	moonrise = parsed_json['moon_phase']['moonrise']['hour'] + ":"
	moonrise += parsed_json['moon_phase']['moonrise']['minute']
	moonrise += ":00"
	print "moonrise time %s" % (moonrise)

	moonset = parsed_json['moon_phase']['moonset']['hour'] + ":"
	moonset += parsed_json['moon_phase']['moonset']['minute']
	moonset += ":00"
	print "moonset time %s" % (moonset)

	MyDateTime = datetime.datetime.now()
	#print datetime.datetime.now()

	date = MyDateTime.strftime("%d/%m/%y")
	print "current date time %s" % (date)

	data = {"weatherinfo" : {}}
	data['weatherinfo']['temp_c'] = temp_c
	data['weatherinfo']['date'] = date
	data['weatherinfo']['weather'] = weather_des
	data['weatherinfo']['precipitation'] = precip_today_metric
	data['weatherinfo']['currtime'] = currtime
	data['weatherinfo']['sunrise'] = sunrise
	data['weatherinfo']['sunset'] = sunset
	data['weatherinfo']['moonrise'] = moonrise
	data['weatherinfo']['moonset'] = moonset
	json_data = json.dumps(data)
	print json_data
	f.close()	

	UARTWrite(json_data)

# Raspberry Pi pin configuration for SSD1351:
RST0 = 5
RST1 = 6
# Note the following are only used with SPI:
DC0 = 24
DC1 = 23

# SPI Port definition. 
SPI_PORT = 0
SPI_DEVICE0 = 0
SPI_DEVICE1 = 1

# 128x96 display instance with hardware SPI:
LCD0 = Adafruit_SSD1351.SSD1351_128_96(rst=RST0, dc=DC0, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE0, max_speed_hz=8000000))
LCD1 = Adafruit_SSD1351.SSD1351_128_96(rst=RST1, dc=DC1, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE1, max_speed_hz=8000000))

# Initialize library.
LCD0.begin()
LCD1.begin()

# Clear display.
LCD0.clear()
LCD1.clear()

## CRC16 temp variable for CRC16 CCIT 
crc = bytearray([0, 0, 0, 0]) 

### UART Write function
def UARTWrite(data):
	# Serial Port open, this is different than in RPI 2 or other RPI devices.
	# There is an issue with the pi3 revision b
	serialport = serial.Serial("/dev/ttyS0", 115200, timeout=0.5) # Baudrate 9600, Timeout 0.5sec
	# Byte Array
	buff = []
	# get bytes from JSON data which are then sent to teensy.
	buff = data.encode()
	#print CRC32().calculate(buff)
	nCRC32 = CRC32().calculate(buff)
	print hex(nCRC32)
	
	# Set CRC16 variable 
	crc[3] = nCRC32 & 0xFF # get low byte from CRC16
	# get high byte from CRC16
	nCRC32 >>= 8
	crc[2] = nCRC32 & 0xFF
	nCRC32 >>= 8
	crc[1] = nCRC32 & 0xFF
	nCRC32 >>= 8
	crc[0] = nCRC32 & 0xFF    
	# Send main message
	print serialport.write(buff) 
	# Send CRC16 buffer
	print serialport.write(crc) 

	# Close Serial Port, so that other routines can use serial instance 
	serialport.close()
	time.sleep(0.25)

# Custom MQTT message callback, if any message is arrived PI, program will call the customCallback.
def customCallback(client, userdata, message):
	# topic is in message.topic, message is in message.payload.
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	
	# create a JSON Object
	ParsingObj = json.loads(message.payload)

	### parse JSON
	print ParsingObj["person"]["imageUrl"]
	imgurl = ParsingObj["person"]["imageUrl"]
	userID = ParsingObj["person"]["userID"]
	locationID = ParsingObj["person"]["locationID"]
	userName = ParsingObj["person"]["userName"]

	# Create image path for Image download on PI
	ScreenImgPath = "Screenimage" + str(userID)
	ScreenImgPath = ScreenImgPath + ".jpg"

	# 
	try: 
		# Open URL, if the url doesn't exist, trace exception
		imgdata = urllib2.urlopen(imgurl)
		# If there is no error get the image
		urllib.urlretrieve(imgurl, ScreenImgPath)
	except urllib2.HTTPError, e:
		print e.code
		return
	except urllib2.URLError, e:
		print e.args
		return

	#Open image using stock using image library 
	image = Image.open(ScreenImgPath).resize((128, 96), Image.ANTIALIAS)

	if userID == 1:# First display module
		LCD0.roughimage(image)
	elif userID == 2: # Second display module
		LCD1.roughimage(image)
	
	# Write Packet mqtt message content
	UARTWrite(message.payload)
		

interval = 1
cycle = 0
Timeout = 10 # 10 sec

def GetWeatherthreadProc(e):
	print('Weather thread proc is started!')
	cycle = 0
	GetWeatherInfo()
	while not e.isSet():
		event_is_set = e.wait(interval)
		cycle = cycle + 1
		if cycle > Timeout:
			cycle = 0
			GetWeatherInfo()


# Start up routine.
# parameters for AWS Mqtt, mainly tested using Mqtt.FX software
host = "a1idvfzc1etc2l.iot.us-west-2.amazonaws.com" # endpoint for AWS IOT thing

# Root ceritficate Path
rootCAPath = "root-CA.crt"
certificatePath = "HouseyTest.cert.pem"
privateKeyPath = "HouseyTest.private.key"


# Configure logging, only for analysing the log of Mqtt client
# (I probably don't need this for now because I've been using MQTT.fx for testing)
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub") # Client name 
# Configure with certificate setting
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect() # Mqtt Client connect 

 # set subscribe topic 
myAWSIoTMQTTClient.subscribe("Home/WeatherRPI/Input1", 1, customCallback)
myAWSIoTMQTTClient.subscribe("Home/WeatherRPI/Input2", 1, customCallback)

time.sleep(2)

# Publish to the output topic in a loop forever
myAWSIoTMQTTClient.publish("Home/WeatherRPI/Output", "Rapsberry Pi Weather Station is Ready!", 0)

myevent = threading.Event()
CurrentThread = threading.Thread(target=GetWeatherthreadProc, args=(myevent,))
CurrentThread.start()

try:
	while True:
		time.sleep(2)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    myevent.set()



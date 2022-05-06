from picamera import PiCamera
from time import sleep
import subprocess as sp
import RPi.GPIO as GPIO
import os
import datetime

from threading import Thread
import time

import requests

url = 'http://ptsv2.com/t/s5an6-1651803830/post'
particleURL = 'https://api.particle.io/v1/devices/e00fce68a9f4ac6593b954a9/speechEventHandler'
access = {"access_token":"123412341234"}

    

# http://ptsv2.com/t/s5an6-1651803830 Logs Post Requests

# Creates a counter for LED Flashing
global cycle
cycle = 0.0

# Setup GPIO Pins and turn on the LED

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
led = GPIO.PWM(18,1000)
led.start(0)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# Method to control the LED state
def controlLED(on, bright=25):
	if on:
		led.ChangeDutyCycle(bright)
	else:
		led.ChangeDutyCycle(0)

# Class for controlling threading of LED animation
class PulseLight:
	# Create Class  
    def __init__(self):
        self._running = True

    # End Class and Turn Off LED
    def terminate(self):  
        self._running = False  
        controlLED(False)


    # Run LED Cycle
    def run(self):
        global cycle
        while self._running:
            time.sleep(.5)
            cycle = cycle + 1.0
            if (cycle % 2) == 0:
            	controlLED(True)
            else:
            	controlLED(False)


controlLED(True)

# Setup the Camera
camera = PiCamera()
#camera.resolution = (1280, 720)
camera.vflip = True
camera.contrast = 40
camera.hflip = True

# Allow Camera to startup
sleep(5);

# Communicate to User that setup is completed
controlLED(False)

# Method for taking and saving photo to file
def takePhoto(name = "current.jpg", dire = "/home/pi/tmp/"):
	date = datetime.datetime.now().strftime('%m-%d-%Y_%H.%M.%S')
	pulse = PulseLight()
	pulseThread = Thread(target=pulse.run) 
	pulseThread.start()
	sleep(0.25)
	fullDir = (dire+date+name)
	camera.capture(fullDir)
	print("Photo saved at " + fullDir)
	pulse.terminate()
	return fullDir

# Code for procesing the photo using ssocr
def processPhoto(path, ssocr_path="ssocr"):
	pulse = PulseLight()
	pulseThread = Thread(target=pulse.run) 
	pulseThread.start()
	print(path)
	desktop = os.path.expanduser("~/")
	sspath = os.path.join(desktop, ssocr_path)
	os.chdir(sspath)
	try:
		output = sp.check_output('./ssocr -T -d -1 '+path, shell=True).decode("utf-8").strip()
		if (output == "8"):
			output = sp.check_output('./ssocr invert -T -d -1 '+path, shell=True).decode("utf-8").strip()

		#output =  output.split("'")[1]
		pulse.terminate()
		controlLED(False)
		return output
	except sp.CalledProcessError as e:
		print(e.output)
		pulse.terminate()
		controlLED(False)
		return ""
	
# Combine Reading and Photo code
def takeReading():
	reading = processPhoto(takePhoto())
	print("Value recorded of: " + reading)
	return reading

# Button Activation Method
def buttonPress():
	reading = processPhoto(takePhoto())
	print("Value recorded of: " + reading)
	postReading(reading)
	
	return reading

# Method for sending HTTP Request
def postReading(value):
	myobj = {'reading': value}
	x = requests.post(url, data = myobj)
	#y = requests.post(particleURL, header=access, data=myobj)
	print(x.text)

# Test Reading
files=["/home/pi/tmp/test1.jpg","/home/pi/tmp/test2.jpg", "/home/pi/tmp/six_digits.png"]
for file in files:
	print("Testing File " + file)
	out = processPhoto(file)
	print("'" + out +"'")
	postReading(out);

# Couple Button Press
#GPIO.add_event_detect(23,GPIO.RISING,callback=buttonPress,bouncetime=300)
while True:
    if GPIO.input(23):
    	buttonPress() 

controlLED(False)


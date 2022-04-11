from picamera import PiCamera
from time import sleep
import subprocess as sp
import RPi.GPIO as GPIO
import os

from threading import Thread
import time

global cycle
cycle = 0.0


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
led = GPIO.PWM(18,1000)
led.start(0)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def controlLED(on, bright=25):
	if on:
		led.ChangeDutyCycle(bright)
	else:
		led.ChangeDutyCycle(0)

class PulseLight:  
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  
        controlLED(False)


    def run(self):
        global cycle
        while self._running:
            time.sleep(.5) #Five second delay
            cycle = cycle + 1.0
            if (cycle % 2) == 0:
            	controlLED(True)
            else:
            	controlLED(False)



controlLED(True)

camera = PiCamera()
#camera.resolution = (1280, 720)
camera.vflip = True
camera.contrast = 40
camera.hflip = True

sleep(5);

controlLED(False)

def takePhoto(name = "current.jpg", dire = "/home/pi/tmp/"):
	pulse = PulseLight()
	pulseThread = Thread(target=pulse.run) 
	pulseThread.start()
	sleep(0.25)
	camera.capture(dire+name)
	print("Photo saved at " + dire + name)
	fullDir = (dire+name)
	pulse.terminate()
	return fullDir

def processPhoto(path, ssocr_path="ssocr"):
	pulse = PulseLight()
	pulseThread = Thread(target=pulse.run) 
	pulseThread.start()
	print(path)
	desktop = os.path.expanduser("~/")
	sspath = os.path.join(desktop, ssocr_path)
	os.chdir(sspath)
	try:
		output = sp.check_output('./ssocr -T '+path, shell=True)
		output =  output.split("'")[1]
		pulse.terminate()
		controlLED(False)
		return ''.join(filter(str.isalnum, output)) 
	except sp.CalledProcessError as e:
		print(e.output)
		pulse.terminate()
		controlLED(False)
		return ""
	

def takeReading(self):
	reading = processPhoto(takePhoto())
	print("Value recorded of: " + reading)
	return reading


GPIO.add_event_detect(23,GPIO.RISING,callback=takeReading,bouncetime=300)
try:  
    while True : pass  
except:
    GPIO.cleanup()  

controlLED(False)


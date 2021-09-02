#!/usr/bin/python3.7

import subprocess
from subprocess import call
import RPi.GPIO as GPIO  
import time
import os
import signal
from datetime import datetime, timedelta
import sys
from threading import Thread
import threading

def thread_function(mins):
    global endtime
    global p
    currenttime = datetime.now()
    endtime = datetime.now() + timedelta(minutes=mins)
    while (currenttime < endtime):
        print("Current Time ", currenttime)
        print("End Time ", endtime)
        currenttime = datetime.now()
        #check_pir(mins)
        time.sleep(1)
    GPIO.remove_event_detect(21)
    #time.sleep(10) # Needs tweaking
    call(["/opt/vc/bin/tvservice", "-o"])
    p.kill()
    time.sleep(30) # Needs tweaking try 10
    GPIO.add_event_detect(21, edge=GPIO.BOTH, callback = cb_radar_switch)

def check_pir(self):
    global endtime
    global p
    global mins
    #i=GPIO.input(21)
    #if i==0: # When output from motion sensor is LOW
    #    print("No person detected.", i)
    #if i==1: # When output from motion sensor is HIGH
    #print("Person detected.", i)
    print("Person detected.")
    callresult = subprocess.run(["/opt/vc/bin/tvservice", "-s"], stdout=subprocess.PIPE)
    if "state 0x2 [TV is off]" in callresult.stdout.decode('utf-8'):
        #GPIO.remove_event_detect(21)
        #time.sleep(10) # Needs tweaking
        call(["/opt/vc/bin/tvservice", "-p"])
        call(["/usr/bin/sudo", "systemctl", "restart", "display-manager"])
        os.environ["DISPLAY"] = ":0.0"
        time.sleep(3)
        p = subprocess.Popen(["/home/pi/photo-frame-code/start-photo-frame-python3.py"])
        #time.sleep(10) # Needs tweaking
        #GPIO.add_event_detect(21, edge=GPIO.BOTH, callback = cb_radar_switch)
        #print("Would turn on system now.")
    else:
        endtime = datetime.now() + timedelta(minutes=mins)

def factory_reset_system(self):
    print("Would factory reset here.")

    # Reset screen off timeout to 15 minutes
    # CODE NOT YET WRITTEN
   
    # Reset any other user configured settings
    # CODE NOT YET WRITTEN
 
    # Replace existing /etc/hosts and /etc/hostname with default factory versions
    #call(["/usr/bin/sudo", "/bin/cp", "/etc/hosts.FACTORY", "/etc/hosts"])
    #call(["/usr/bin/sudo", "/bin/cp", "/etc/hostname.FACTORY", "/etc/hostname"])
    
    # Enable both dnsmasq and hostapd to facilitate initial setup
    #call(["/usr/bin/sudo", "/usr/sbin/update-rc.d", "dnsmasq", "enable"])
    #call(["/usr/bin/sudo", "/usr/sbin/update-rc.d", "hostapd", "enable"])
    
    # Finally, reboot the Raspberry Pi with the restored factory configuration
    #call(["/usr/bin/sudo", "/sbin/reboot"])

def halt_system(self):
    call(["/usr/bin/sudo", "/sbin/halt"])

class ButtonHandler(threading.Thread):
    def __init__(self, pin, func, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)
        
        if (
            ((pinval == 0 and self.lastpinval == 1) and
            (self.edge in ['falling', 'both'])) or
            ((pinval == 1 and self.lastpinval == 0) and
            (self.edge in ['rising', 'both']))
        ):
            self.func(*args)

        self.lastpinval = pinval
        self.lock.release()

def setup():
    global endtime
    global mins
    global p
    global cb_radar_switch
    global halt_switch_port
    global factory_reset_switch_port
 
    halt_switch_port = 2
    factory_reset_switch_port = 26

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(halt_switch_port, GPIO.IN) # Read output from halt switch
    GPIO.setup(factory_reset_switch_port, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Read output from factory reset switch
    cb_halt_switch = ButtonHandler(halt_switch_port, halt_system, edge='falling', bouncetime=50)
    cb_halt_switch.start()
    cb_factory_reset_switch = ButtonHandler(factory_reset_switch_port, factory_reset_system, edge='falling', bouncetime=50)
    cb_factory_reset_switch.start()   
    GPIO.add_event_detect(halt_switch_port, edge=GPIO.FALLING, callback = cb_halt_switch)
    GPIO.add_event_detect(factory_reset_switch_port, edge=GPIO.FALLING, callback = cb_factory_reset_switch)
    
    mins = 30

    call(["/opt/vc/bin/tvservice", "-o"])
    
    #GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # Read output from PIR motion sensor
    #GPIO.setup(halt_switch_port, GPIO.IN) # Read output from halt switch
    #GPIO.setup(factory_reset_switch_port, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Read output from factory reset switch
    cb_radar_switch = ButtonHandler(21, check_pir, edge='both', bouncetime=50)
    cb_radar_switch.start()
    #cb_halt_switch = ButtonHandler(halt_switch_port, halt_system, edge='falling', bouncetime=50)
    #cb_halt_switch.start()
    #cb_factory_reset_switch = ButtonHandler(factory_reset_switch_port, factory_reset_system, edge='falling', bouncetime=50)
    #cb_factory_reset_switch.start() 
    time.sleep(30) # Needs tweaking try 10
    GPIO.add_event_detect(21, edge=GPIO.BOTH, callback = cb_radar_switch)
    #GPIO.add_event_detect(halt_switch_port, edge=GPIO.FALLING, callback = cb_halt_switch)
    #GPIO.add_event_detect(factory_reset_switch_port, edge=GPIO.FALLING, callback = cb_factory_reset_switch)
 
    while True:
        thread_function(mins)

setup()

#!/usr/bin/python

#  Copyright (C) 2013
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
#  Authors : Roberto Calvo <rocapal at gmail dot com>
#            Dan Mandle

import os
from gps import *
from time import *
import time
import threading
from sys import stdout 
from temp import read_temp
from RBPiCamera import snap_photo
import RPi.GPIO as GPIO
import signal

gpsd = None 

RED = 23
GREEN = 24
BLUE = 25
 
os.system('clear') 
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd 
    gpsd = gps(mode=WATCH_ENABLE) 
    self.current_value = None
    self.running = True 
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next()


def init ():
  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(RED, GPIO.OUT)
  GPIO.setup(GREEN, GPIO.OUT)
  GPIO.setup(BLUE, GPIO.OUT)

  for i in range(0,2):
    GPIO.output(RED,False)
    GPIO.output(GREEN,True)
    GPIO.output(BLUE,True)
    time.sleep(1)
    GPIO.output(RED,True)
    GPIO.output(GREEN,False)
    GPIO.output(BLUE,True)
    time.sleep(1)

  GPIO.output(RED,True)
  GPIO.output(GREEN,True)
  GPIO.output(BLUE,True)

def led_gps_search (status):
  GPIO.output(RED,True)
  GPIO.output(GREEN,True)
  GPIO.output(BLUE,status)

def led_data (status):
  GPIO.output(RED,True)
  GPIO.output(GREEN,status)
  GPIO.output(BLUE,True)

def save_data (file_name, temp):

  data_file = open(file_name, 'w')  

  data_file.write(gpsd.utc + "\n")
  data_file.write(str(gpsd.fix.latitude) + "\n")
  data_file.write(str(gpsd.fix.longitude) + "\n")
  data_file.write(str(gpsd.fix.altitude) + "\n")
  data_file.write(str(gpsd.fix.speed) + "\n")
  data_file.write(str(temp[0]) + "\n")

  data_file.close()

def get_file_name (datetime):

  try:
    date = datetime.split("T")[0].replace("-",".")
    time = datetime.split("T")[1].split(".")[0].replace(":",".")
    return date + "-" + time
  except:
    print "Not well formed the filename with: " + datetime
    return None


def func (signum, frame):
  print "SIGTERM"
  sys.exit()

if __name__ == '__main__':

  signal.signal(signal.SIGTERM, func)	

  gpsp = GpsPoller()

  try:
    init()
    gpsp.start()

    list = ['|','/','-','\\']
    c = 0

    SLEEP_DATA = 90
    DIR = "/home/pi/WTLv2-data/"

    while True:

      if (gpsd.fix.mode	== MODE_NO_FIX):
        stdout.write("\rWaiting for FIX: %s" % list[c])
        
        c = c+1
        if (c>2):
          c=0

        stdout.flush()
        led_gps_search(False)
        time.sleep(1)        
        led_gps_search(True)
        time.sleep(1)

      else:

        os.system('clear')
        led_data(False);

        print
        print ' GPS reading'
        print '----------------------------------------'
        print 'latitude    ' , gpsd.fix.latitude
        print 'longitude   ' , gpsd.fix.longitude
        print 'time utc    ' , gpsd.utc
        print 'altitude (m)' , gpsd.fix.altitude
        print 'speed (m/s) ' , gpsd.fix.speed
        print 'mode        ' , gpsd.fix.mode
        print ' '

        # Get Temperature
        temp =  read_temp()
        print ("Temperature: %.2f" % temp[0])

        # Build filename to save data
        file_name = get_file_name(gpsd.utc)

        # Save the picture
        args = []


        args.append({"name": "width" , "argument": "1920"});
        args.append({"name": "height", "argument": "1080"});
	args.append({"name": "exposure", "argument": "sports"});
        args.append({"name": "hflip", "argument": "true"});
        args.append({"name": "vflip", "argument": "true"});

        snap_photo(args, DIR + file_name + "I")

        # Save the data
        save_data(DIR + file_name + "D", temp)

        print "Save data and picture: " + DIR + file_name + "[I|D]"
        
        os.system("sync")
        time.sleep(1)
        led_data(True)
        time.sleep(SLEEP_DATA) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    
    GPIO.output(RED,True)
    GPIO.output(GREEN,True)
    GPIO.output(BLUE,True)
    if gpsp.is_alive():
      gpsp.running = False
      gpsp.join()

  print "Done.\nExiting."

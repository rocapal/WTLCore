#!/usr/bin/env python

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


from subprocess import call
import StringIO
from json import JSONEncoder
from django.utils import simplejson
import socket
import threading

IMAGE_FILE_PATH = "/tmp/image.jpg"

RBPI_PHOTO_COMMAND = "raspistill"
RBPI_VIDEO_COMMAND = "raspivid"

VLC_STREAMING_COMMAND = " | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264"
VLC_STREAMING_URL = "http://%s:8090/"

control_streaming_th = None 

disable_args = ['none','false', 'off']



def parse_args (args_list, timeout = 0):

	args = ""

	if "timeout" is not args_list:
		args = args + "--timeout " + str(timeout) + " "


	for arg in args_list:
		if (arg["argument"] == "true"):
			args = args + "--" + arg["name"] + " "
			continue
		if (arg["argument"] in disable_args):
			continue
                        
		args = args + "--" + arg["name"] + " " + arg["argument"] + " "

	return args

def snap_photo (args_list, image_path = None):

	res_image = ""
	if (image_path != None):
		res_image = image_path
	else:
		res_image = IMAGE_FILE_PATH
	
	args = "--output " + res_image + " "  + parse_args(args_list, 2500)

	command = RBPI_PHOTO_COMMAND + " " + args
	print command
	return_code = call(command, shell=True);
	if (return_code == 0):
		return res_image 
	else:
		return None


def launch_cmd (command):
	code = call (command, shell=True)

def start_streaming (args_list):

	global control_streaming_th 
	res = {}
	args = " -o - " + parse_args(args_list, 9999999)
	command = RBPI_VIDEO_COMMAND + " " + args + " " + VLC_STREAMING_COMMAND

	print command 

	try:
		if (control_streaming_th == None):
			control_streaming_th = 1
			streaming_th  = threading.Thread(target = launch_cmd, args=[command])
			streaming_th.setDaemon(True)
			streaming_th.start()

		res["code"] = 200
		res["streaming_url"] = VLC_STREAMING_URL % (get_ip())
		
	except:
		res["code"] = 500
		res["msg"] = "Error while streaming was initialized!"
		res["streaming_url"] = ""
		

	return res

def stop_streaming():

	global control_streaming_th 

	cmds = {'vlc',RBPI_VIDEO_COMMAND}

	for cmd in cmds:
		print "killing " + cmd
		kill_command = "ps aux | grep " + cmd + " | grep -v grep | tr -s ' ' | cut -d' ' -f2 | tr -s '\n' ' ' | sed -e s/^/kill\ -9\ /g | bash"
		call (kill_command, shell=True)

	control_streaming_th = None



def get_ip ():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("gmail.com",80))
	ip = (s.getsockname()[0])
	s.close()
	return ip


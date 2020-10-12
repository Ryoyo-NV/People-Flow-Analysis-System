#!/usr/bin/env python3

#pylint: disable=wrong-import-position
import sys

sys.path.insert(0, '/*')

import math
import queue
import time
import threading
import constant
import send_message as sm
import config as cf
from os import path
from timeit import default_timer as timer

# class MessageManager
# Description: Alert message manager
# 		Forward alert message to send_message.py
# Paremeter: MessageSender
# Return value: None
class MessageManager(sm.MessageSender):

	__message_queue = []			# Holds alert message
	__queue_copy = []				# Holds the message queue copy
	__message_manager = None 		# Holds the instance of MessageManager

	__state = None					# Initial state is idle

	is_client_iothub_ok = False     # Holds flag if client connection for iothub is OK
	is_client_mobile_ok = False     # Holds flag if client connection for mobile is OK

	__user_config = None			# Holds the user configuration instance

	# function __init__()
	# Description: class constructor
	# Paremeter: None
	# Return value: None
	def __init__(self, config=None):
		"""Class constructor"""

		# Check if config is none
		if config is None:
			# Initialize config
			config = cf.Config()	

		# Check message manager is none
		if self.__message_manager is None:

			# Set user configuration instance
			self.__user_config = config
			# Make instance of MessageSender
			sm.MessageSender.__init__(self, config)
			# Make instance of Message Manager
			self.__message_manager = super().__init__(config);

			# Global variable for checking connection status during thread processing
			global is_client_iothub_ok
			global is_client_mobile_ok
			is_client_iothub_ok = True    # Set initially to OK
			is_client_mobile_ok = True    # Set initially to OK

			self.__state = constant.STATE_IDLE

	# function add()
	# Description: Function that will be triggered when dwell time exceeds
	# 		Params received are added to message stack pool. FIFO is followed.
	# Paremeter: self, trackid, dwell_time, location, image
	# Return value: RETURN_OK, RETURN_NG
	def add(self, track_id, dwell_time, location, image = None):
		"""Add alert message to message queue"""

		# Check if the message queue item count is below the maximum
		if constant.MAX_ALERT_CNT > len(self.__message_queue):

			# Add new alert message to message queue with details:
			# track_id, dwell_time, location, image
			data = track_id, dwell_time, location, image
			self.__message_queue.append(data)

			# Alert message is added
			result = constant.RETURN_OK

		else:

			# Unable to add more alert message
			result = constant.RETURN_NG

		return result

	# function start()
	# Description: Function that start the message manager execution
	# Paremeter: None
	# Return value: None
	def start(self):
		"""Start the message manager execution"""

		# Check if the state is idle
		if constant.STATE_IDLE == self.__state:

			# make state busy
			constant.__state = constant.STATE_BUSY

			# start process
			self.__run()

			# make state idle
			self.__state = constant.STATE_IDLE

		# Check if the state is busy
		elif constant.STATE_BUSY == self.__state:

			print("Can't start. Message manager is busy at this moment.")

		# Check if the state has error
		elif constant.STATE_ERROR == self.__state:

			print("Can't start. Client connections cannot established.")

	# function __run()
	# Description: Function to run process
	# Paremeter: None
	# Return value: None
	def __run(self):
		"""Run message manager process"""

		# clear queue copy before use
		self.__queue_copy.clear()

		# Check if message queue is not empty
		while 0 < len(self.__message_queue):

			# Move alert from message queue to queue copy
			self.__queue_copy.append(self.__message_queue.pop(0))

		# Process every alert message to send them
		for message in self.__queue_copy:

			# Execute each thread per alert
			x = threading.Thread(target=self.send, args=(message,))
			x.start()

	# function send()
	# Description: Function to call send_message function to send message
	# Paremeter: message
	# Return value: None
	def send(self, message):
		"""Send alert message to iot hub and mobile"""

		# Connection status for alert thread processing
		global is_client_iothub_ok
		global is_client_mobile_ok

		# get message details
		track_id, dwell_time, location, image = message
		x, y = location

		num = 0		# number of attempt to send message to IoT Hub

		print("===============================================================") 
		print("Alert Message:", message)
		print("Destination: IoT Hub")

		# put retry limit when send alert failed
		while constant.MAX_RETRY > num:

			# add attempt
			num = num + 1 
			# send alert message for IoT hub
			print(">>> Attempt:", num,", Sending...")   
			if constant.RETURN_OK == self.iothub_client_send_message(dwell_time, track_id, x, y):

				print("Message sent!")
				# Set iothub connection status to ok
				is_client_iothub_ok = True
				break

			else:

				# Set iothub connection status to error
				is_client_iothub_ok = False
				print("Message sending failed!")

		num = 0		# number of attempt to send message to mobile

		print("===============================================================") 
		print(">>> Alert Message:", message)
		print("Destination: Mobile")

		# put retry limit when send alert failed
		while constant.MAX_RETRY > num:

			# add attempt
			num = num + 1
			# send alert message for mobile
			print("Sending message to mobile. Attempt: ", num)  
			if constant.RETURN_OK == self.mobile_client_send_message(dwell_time, track_id, x, y):

				print("Message sent!")
				# Set iothub connection status to ok
				is_client_mobile_ok = True
				break

			else:

				# Set iothub connection status to error
				is_client_mobile_ok = False
				print("Message sending failed!")
				

	# function is_client_iothub_ok()
	# Description: Function that return the status of iothub client connection
	# Paremeter: None
	# Return value: is_client_iothub_ok
	def is_iothub_conn_ok(self):
		"""Return true if the iothub client connection is OK. False if error occurred"""
		global is_client_iothub_ok
		return is_client_iothub_ok

	# function is_mobile_conn_ok()
	# Description: Function that return the status of mobile client connection
	# Paremeter: None
	# Return value: is_client_mobile_ok
	def is_mobile_conn_ok(self):
		"""Return true if the mobile client connection is OK. False if error occurred"""
		global is_client_mobile_ok
		return is_client_mobile_ok

	# function getUserConfig()
	# Description: Function that returns the user configuration instance
	# Paremeter: None
	# Return value: __user_config
	def getUserConfig(self):
		"""Return the user configuraiton instance"""
		return self.__user_config







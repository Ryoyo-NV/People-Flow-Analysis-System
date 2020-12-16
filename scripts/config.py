#!/usr/bin/env python3

#pylint: disable=wrong-import-position
import configparser
import constant
import os

# class Config
# Description: PFA user configuration
# Paremeter: None
# Return value: None
class Config:
	"""User configuration"""

	FILE_PATH_STR = "../config/pfa_config.ini" 	# Config file path

	# function __init__
	# Description: class constructor
	# Paremeter: None
	# Return value: None
	def __init__(self):
		"""Class constructor"""
		self.__init_config()

	# function __init_config
	# Description: Function to initialize config
	# Paremeter: None
	# Return value: None
	def __init_config(self):
		"""Configuration settings"""

		# User config option list
		HOST_NAME = "host_name"
		DEVICE_ID = "device_id"
		SHARED_ACCESS_KEY = "shared_access_key"
		HOST = "host"
		PORT = "port"
		AR_WIDTH = "ar_width"
		AR_HEIGHT = "ar_height"
		PIXEL_PER_FEET = "pixel_per_feet"
		DWELL_LIMIT = "dwell_limit"
		DWELL_TIME_AVERAGE = "dwell_time_average"
		CAM_MODE = "cam_mode"

		# Set config file
		config = configparser.ConfigParser()

		# Check if config file is set
		if os.path.isfile(self.FILE_PATH_STR) is True:
			config.read(self.FILE_PATH_STR)
			config.optionxform = str 			# make options change to lower case
		else:
			# Since config file cannot be used, default values will be set
			print("[ERROR] Problem encountered upon opening the user config file.")
			print("[INFO] Please verify [{}]".format(self.FILE_PATH_STR))
			self.__set_defaults()
			return
		
		# read values from a section
		try:

			# Set iothub connection string from user config
			iot_hub_hostname = config.get('iot_hub_client_setting', HOST_NAME)
			iot_hub_device_id = config.get('iot_hub_client_setting', DEVICE_ID)
			iothub_shared_access_key = config.get('iot_hub_client_setting', SHARED_ACCESS_KEY)

		except:

			# Set default connection string
			self.__connection_string = "HostName={};DeviceId={};SharedAccessKey={}".format(\
				constant.HOST_NAME, constant.DEVICE_ID, constant.SHARED_ACCESS_KEY)

			print("[ERROR] Config set for CONNECTION_STRING is invalid! Default {} is used."\
				.format(self.__connection_string))

		else:

			self.__connection_string = "HostName={};DeviceId={};SharedAccessKey={}".format(\
				iot_hub_hostname, iot_hub_device_id, iothub_shared_access_key)

			print("CONNECTION_STRING config is set successfully!")

		finally:

			pass

		############################################################################################

		try:

			# Set mobile host from user config
			self.__host = config.get('mobile_client_setting', HOST)

		except:

			print("[ERROR] Config set for HOST is invalid! Default {} is used."\
				.format(constant.HOST))
			# Set default host
			self.__host = constant.HOST

		else:

			print("Mobile HOST config is set successfully!")

		finally:

			pass

		############################################################################################

		try:

			# Set mobile port from user config
			self.__port = config.getint('mobile_client_setting', PORT)

		except:

			print("[ERROR] Config set for PORT is invalid! Default {} is used."\
				.format(constant.PORT))
			# Set default port
			self.__port = constant.PORT

		else:

			print("Mobile PORT config is set successfully!")

		finally:

			pass

		############################################################################################
 
		try:

			# Set aspect ratio width from user config
			self.__ar_width = self.__get_valid_ar_width(\
				config.getint('display_setting', AR_WIDTH))

		except:

			print("[ERROR] Config set for AR_WIDTH is invalid! Default {} is used."\
				.format(constant.AR_WIDTH))
			# Set default aspect ration width
			self.__ar_width = constant.AR_WIDTH

		else:

			print("AR_WIDTH config is set successfully!")

		finally:

			pass

		############################################################################################

		try:

			# Set aspect ratio height from user config
			self.__ar_height = self.__get_valid_ar_height(\
				config.getint('display_setting', AR_HEIGHT))

		except:

			print("[ERROR] Config set for AR_HEIGHT is invalid! Default {} is used."\
				.format(constant.AR_HEIGHT))
			# Set default aspect ration height
			self.__ar_height = constant.AR_HEIGHT

		else:

			print("AR_HEIGHT config is set successfully!")

		finally:

			pass


		############################################################################################

		try:

			# Set pixel per feet from user config
			self.__px_per_ft = self.__get_valid_px_per_ft(\
				config.getint('display_setting', PIXEL_PER_FEET))

		except:

			print("[ERROR] Config set for PIXEL_PER_FEET is invalid! Default {} is used."\
				.format(constant.PIXEL_PER_FEET))
			# Set default pixel per feet
			self.__px_per_ft = constant.PIXEL_PER_FEET

		else:

			print("PIXEL_PER_FEET config is set successfully!")

		finally:

			pass


		############################################################################################

		# Set aspect ratio
		self.__aspect_ratio = self.__ar_height, self.__ar_width

		############################################################################################

		try:

			# Set dwell time limit in 1 location from user config
			self.__dwell_limit = config.getint('alert_setting', DWELL_LIMIT)

		except:

			print("[ERROR] Config set for DWELL_LIMIT is invalid! Default {} is used."\
				.format(constant.DWELL_LIMIT))
			# Set default dwell time in 1 location
			self.__dwell_limit = constant.DWELL_LIMIT

		else:

			print("DWELL_LIMIT config is set successfully!")

		finally:

			pass


		############################################################################################

		try:

			# Set dwell time average from user config. Average of a location and its neighbors.
			ave_percent = config.getfloat('alert_setting', DWELL_TIME_AVERAGE)
			
		except:

			print("[ERROR] Config set for DWELL_TIME_AVERAGE is invalid! Default {} is used."\
				.format(constant.DWELL_AVERAGE_LIMIT))
			# Set default dwell time average
			self.__dwell_time_average = constant.DWELL_AVERAGE_LIMIT

		else:

			self.__dwell_time_average = (self.__dwell_limit * ave_percent)
			print("DWELL_TIME_AVERAGE config is set successfully!")

		finally:

			pass

		############################################################################################

		try:

			# Set camera mode from user config
			cam_mode = config.getfloat('other_setting', CAM_MODE)
			
		except:

			print("[ERROR] Config set for CAM_MODE is invalid! Default {} is used."\
				.format(constant.CAM_MODE))
			# Set default camera mode
			self.__cam_mode = constant.CAM_MODE

		else:

			# Check if camera mode is valid
			self.__cam_mode = self.__get_valid_cam_mode(cam_mode)
			print("CAM_MODE config is set successfully!")

		finally:

			pass


		############################################################################################
		
	# function get_iot_hub_conn_string
	# Description: Function that returns the iothub connection string from user config
	# Paremeter: None
	# Return value: __connection_string
	def get_iot_hub_conn_string(self):
		"""Returns iothub connection string"""

		return self.__connection_string

	# function get_mobile_conn_host
	# Description: Function that returns the mobile connection host from user config
	# Paremeter: None
	# Return value: __host
	def get_mobile_conn_host(self):
		"""Returns host for mobile connection"""

		return self.__host

	# function get_mobile_conn_port
	# Description: Function that returns the mobile connection port from user config
	# Paremeter: None
	# Return value: __port
	def get_mobile_conn_port(self):
		"""Returns port for mobile connection"""

		return self.__port

	# function get_ar_width
	# Description: Function that returns the aspect ratio width from user config
	# Paremeter: None
	# Return value: __ar_width
	def get_ar_width(self):
		"""Returns aspect ratio width"""

		return self.__ar_width

	# function get_ar_height
	# Description: Function that returns the aspect ratio heigh from user config
	# Paremeter: None
	# Return value: __ar_height
	def get_ar_height(self):
		"""Returns aspect ratio height"""

		return self.__ar_height

	# function get_px_per_ft
	# Description: Function that returns the pixel per feet from user config
	# Paremeter: None
	# Return value: __px_per_ft
	def get_px_per_ft(self):
		"""Returns pixel per feet"""

		return self.__px_per_ft

	# function get_dwell_limit
	# Description: Function that returns the dwell time limit from user config
	# Paremeter: None
	# Return value: __dwell_limit
	def get_dwell_limit(self):
		"""Returns dwell time limit"""

		return self.__dwell_limit

	# function get_dwell_time_average
	# Description: Function that returns the dwell time average from user config
	# Paremeter: None
	# Return value: __dwell_time_average
	def get_dwell_time_average(self):
		"""Returns dwell time average threshold"""

		return self.__dwell_time_average

	# function get_cam_mode
	# Description: Function that returns the camera mode from user config
	# Paremeter: None
	# Return value: __cam_mode
	def get_cam_mode(self):
		"""Returns camera mode"""

		return self.__cam_mode

	# function get_aspect_ratio
	# Description: Function that returns the aspect ratio from user config
	# Paremeter: None
	# Return value: __aspect_ratio
	def get_aspect_ratio(self):
		"""Returns aspect ratio"""

		return self.__aspect_ratio

	# function __get_valid_ar_width
	# Description: Function that serves as a guard for aspect ratio width
	# Paremeter: None
	# Return value: width
	def __get_valid_ar_width(self, width):
		"""Min/Max guards for aspect ration width"""

		if constant.AR_WIDTH_MIN > width:
			width = constant.AR_WIDTH_MIN
		elif constant.AR_WIDTH_MAX < width:
			width = constant.AR_WIDTH_MAX

		return width

	# function __get_valid_ar_height
	# Description: Function that serves as a guard for aspect ratio height
	# Paremeter: None
	# Return value: height
	def __get_valid_ar_height(self, height):
		"""Min/Max guards for aspect ration height"""

		if constant.AR_HEIGHT_MIN > height:
			height = constant.AR_HEIGHT_MIN
		elif constant.AR_HEIGHT_MAX < height:
			height = constant.AR_HEIGHT_MAX

		return height

	# function __get_valid_px_per_ft
	# Description: Function that serves as a guard for pixel per feet
	# Paremeter: None
	# Return value: px
	def __get_valid_px_per_ft(self, px):
		"""Min/Max guards for pixel per feet"""

		if constant.PX_PER_FT_MIN > px:
			px = constant.PX_PER_FT_MIN
		elif constant.PX_PER_FT_MAX < px:
			px = constant.PX_PER_FT_MAX

		return px

	# function __get_valid_cam_mode
	# Description: Function that serves as a guard for camera mode
	# Paremeter: None
	# Return value: px
	def __get_valid_cam_mode(self, cam_mode):
		"""Guards for camera mode"""

		if constant.USB_CAM_MODE == cam_mode or \
			constant.RPI_CAM_MODE == cam_mode:
			pass
		else:
			# Set default 
			cam_mode = constant.CAM_MODE

		return cam_mode

	# function __set_defaults
	# Description: Function that set default for all config settings
	# Paremeter: None
	# Return value: None
	def __set_defaults(self):
		"""Default settings"""

		# Set default values since user config cannot use
		self.__connection_string = "HostName={};DeviceId={};SharedAccessKey={}".format(\
				constant.HOST_NAME, constant.DEVICE_ID, constant.SHARED_ACCESS_KEY)
		self.__host = constant.HOST
		self.__port = constant.PORT
		self.__ar_width = constant.AR_WIDTH
		self.__ar_height = constant.AR_HEIGHT
		self.__px_per_ft = constant.PIXEL_PER_FEET
		self.__aspect_ratio = self.__ar_height, self.__ar_width 
		self.__dwell_limit = constant.DWELL_LIMIT
		self.__dwell_time_average = constant.DWELL_AVERAGE_LIMIT
		self.__cam_mode = constant.CAM_MODE

		print("[INFO] Config default settings are used")

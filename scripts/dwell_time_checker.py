#!/usr/bin/env python3

#pylint: disable=wrong-import-position
import message_manager as mm
import config as conf
import constant

from timeit import default_timer as timer
from datetime import timezone, datetime

# class DwellTimeChecker()
# Description: Handles the dwell time computation
# Paremeter: None
# Return value: None
class DwellTimeChecker():

	__dwell_map = None 		 # Holds dwell map for computation
	__message_manager = None # Holds the message manager instance

	__reset_request_list = []   # Holds the list of track id for resetting dwell time

	# function __init__()
	# Description: class constructor
	# Paremeter: None
	# Return value: None
	def __init__(self, message_manager):
		"""Class constructor"""

		# dwell map initialization with TrackMap
		self.__dwell_map = self.TrackMap(message_manager)
		
		# pass instance of MessageManager class
		self.__message_manager = message_manager

	# function input()
	# Description: Function that call the data input
	#       Received data from tracker.
	# Paremeter: data[]
	# Return value: RETURN_OK, RETURN_NG
	def input(self, data):
		"""RETURN_OK, RETURN_NG, it will be used to detect if the adding of data is succes or not"""

		# Return NG when no data
		# Return NG when data is empty
		if data is None or 0 >= len(data):

			return constant.RETURN_NG

		# Copy data to local
		new_data = data.copy()

		# Check every data
		while 0 < len(new_data):

			# Get the track id data
			new_data, track_data = self.__get_track_id_data(new_data)

			# Run checker for the track id with the most hits transform location
			self.__add_data(track_data)		

		# Call run_checker to start computation
		self.run_checker()

		# Start message_manager process
		self.__message_manager.start()

		return constant.RETURN_OK

	# function __add_data()
	# Description: Function to add data to dwell map
	# Paremeter: new_data
	# Return value: None
	def __add_data(self, new_data):
		"""Add data to dwell map: track id, location, dwell time"""

		# Breakdown new data
		track_id, loc_raw, loc_trans = new_data

		# Skip adding process if track id is in alert mode
		if track_id in self.get_alert_list():
			return

		# Register new track id
		self.__dwell_map.add_track_id(track_id)

		# Add dwell time
		self.__dwell_map.add_dwell_time(track_id, loc_raw, loc_trans)


	# function run_checker()
	# Description: Function to dwell time computation process
	# Paremeter: None
	# Return value: None
	def run_checker(self):

		# Call the function that will do computation
		self.__dwell_map.compute_average()

	# function remove_alert
	# Description: Function to remove track id in alert list
	# Paremeter: track_id
	# Return value: RETURN_OK, RETURN_NG
	def remove_alert(self, track_id):
		"""Remove track id on alert list"""

		# Return NG if track_id is None
		if track_id is None:

			print("Track_id is None")
			return constant.RETURN_NG

		# Check if the track id is in the alert list
		if track_id in self.get_alert_list():

			# Check if the track id is in the reset alert request list
			if track_id in self.__reset_request_list:
				pass				
			else:
				# Add alert track id to request list
				self.__reset_request_list.append(track_id)

			result = constant.RETURN_OK

		else:

			print("[Error]track id is not in alert list")
			result = constant.RETURN_NG

		return result

	# function get_alert_list
	# Description: Function to return the alert list from DwellTimeChecker
	# Paremeter: None
	# Return value: __alert_id_list
	def get_alert_list(self):
		"""Function that returns the alert id list"""

		return self.__dwell_map.get_alert_list()

	# function get_alert_flag
	# Description: Function that check if the track id has alert
	# Paremeter: track_id
	# Return value: True, False
	def get_alert_flag(self, track_id):

		# Check if track id is in the alert list
		if track_id in self.__dwell_map.get_alert_list():

			# Check if track id is in the alert reset request list
			if track_id in self.__reset_request_list:

				# Remove dwell time record
				del self.__dwell_map[track_id]

				# Remove track id from alert reset list
				self.__reset_request_list.remove(track_id)

				# Remove track id from alert list
				self.__dwell_map.remove_alert_from_list(track_id)

				# Alert has been reset
				result = False

			else:

				# Track id has alert
				result = True
			
		else:
			# Track id has no alert
			result = False

		return result

	# function __get_track_id_data
	# Description: Function that get the track id data with the most hit transfrom location only
	# Paremeter: t_data
	# Return value: data_left, (track_id, t_loc_raws[r_loc_trans], r_loc_trans)
	def __get_track_id_data(self, t_data):
		"""Get the track id data with the most hit transform location"""

		t_summary = DwellTimeChecker.Map()	# Holds the list of transform location hits
		t_loc_raws = DwellTimeChecker.Map()	# Holds the list of raw location per transform location
		data_left = []						# Holds the non-target data
		track_id = t_data[0][0]				# Holds the target track id
		index = 0							# Starting index

		# Check each data
		while index < len(t_data):

			# Breakdown data to track id, raw location, transform location
			t_track_id, t_loc_raw, t_loc_trans = t_data[index]

			# Check if the target track id
			if t_track_id == track_id:

				# Check if the transform location is already added to summary
				if t_loc_trans in t_summary:
					# Add hits
					t_summary[t_loc_trans] = t_summary[t_loc_trans] + 1
				else:
					# Add the transform location with initial 1 hit
					t_summary[t_loc_trans] = 1
					# Add raw location
					t_loc_raws[t_loc_trans] = t_loc_raw

			else:

				# Add non-target data. Data with different track id
				data_left.append(t_data[index])

			# Move to next index
			index = index + 1

		# Sort the summary by the number of hits
		sort_result = sorted(t_summary.items(), key=lambda x: x[1])

		# Get the transform location with the most hits.
		r_loc_trans, _ = sort_result.pop()

		return data_left, (track_id, t_loc_raws[r_loc_trans], r_loc_trans)



	# class DwellMap()
	# Description: Class acts as a Vector with key and value
	# Paremeter: None
	# Return value: None
	class Map(dict):

	    # function __init__()
		# Description: class constructor
		# Paremeter: None
		# Return value: None
		def __init__(self):
			"""class constructor"""

	    	# Get dictionary instance
			self = dict()  
	          
	    # function add_to_map()
		# Description: Function that will add new key and value
		# Paremeter: key, value
		# Return value: None
		def add_to_map(self, key, value):
			""""add new item(key,value) to dwell map"""

			# Add new item 
			self[key] = value

	# class TrackMap()
	# Description: Class acts as a Vector with key and value
	# Paremeter: None
	# Return value: None
	class TrackMap(Map):

		__corners = None		 # Holds all corner location
		__sides = None			 # Holds all side location
		__insides = None		 # Holds all inside location

		__alert_id_list = []	 # Holds the track id list with alert
		__message_manager = None # Holds instance of message manager

	    # function __init__()
		# Description: class constructor
		# Paremeter: None
		# Return value: None
		def __init__(self, message_manager):
			"""class constructor"""

	    	# Get dictionary instance
			super().__init__()

			# Set message manager instance
			self.__message_manager = message_manager

			# get user config instance
			config = message_manager.getUserConfig()

			# set user configurations
			self.__conf_dwell_time_limit = config.get_dwell_limit()
			self.__conf_dwell_time_average = config.get_dwell_time_average()

			# to identify corners, sides, insides and their corresponding neighbors
			self.__init_positions()

		# function __init_positions()
		# Description: Function to initialize every category map: __corners, __sides, __insides
		# Paremeter: None
		# Return value: None
		def __init_positions(self):
			"""Initialize __corners, __sides, __insides"""

			# Get instance per category map
			self.__corners = DwellTimeChecker.Map()
			self.__sides = DwellTimeChecker.Map()
			self.__insides = DwellTimeChecker.Map()

			# Fill-in every category map
			self.__get_corners()
			self.__get_sides()
			self.__get_insides()

		# function add_dwell_time()
		# Description: Function that add dwell time
		# Paremeter: None
		# Return value: None
		def add_dwell_time(self, track_id, loc_raw, loc_trans):
			"""Increment dwell time by 1 sec"""

			# Skip when track id is None
			if track_id is None:
				return

			# Skip when location is None
			if loc_trans is None:
				return

			# Skip when raw location is None
			if loc_raw is None:
				return

			# Skip when x or y is not valid
			x, y = loc_trans
			if x < constant.X_MIN or \
				x > constant.X_MAX or \
				y < constant.Y_MIN or \
				y > constant.Y_MAX:
				return

			# Skip when track id has alert
			if track_id in self.__alert_id_list:
				return

			if track_id in self.keys():
				v_map = self[track_id]
				_, dwell_time, dwell_average = v_map[loc_trans]

				# Check if dwell time exceeds limit
				dwell_time = dwell_time + 1
				if dwell_time > self.__conf_dwell_time_limit:
					# Add track id to the alert list
					self.__alert_id_list.append(track_id)
					
					# date and time with timezone
					dt_now = datetime.now(tz=timezone.utc)
					time_now = dt_now.strftime(constant.TIME_STAMP_STR)

					# Add alert
					self.__message_manager.add(track_id, time_now, loc_raw)

				else:
					# Save dwell time
					v_map[loc_trans] = loc_raw, dwell_time, dwell_average


		# function add_track_id()
		# Description: Function that will register track id and create grid for it
		# Paremeter: track
		# Return value: None
		def add_track_id(self, track_id):
			"""Add track id and create grid mapping of all location"""

			# Check if track_id is existing
			if track_id not in self.keys():
				# Create grid with complete locations for track id.
				# It will be save as v_map
				value = self.__create_grid()
				# Set grid to track id
				self[track_id] = value

		# function __create_grid()
		# Description: Function that will create a grid with complete locations
		# Paremeter: None
		# Return value: v_map
		def __create_grid(self):
			"""Create grid mapping of all location"""

			# Set x, y max range
			x_max = constant.X_MAX
			y_max = constant.Y_MAX

			# Initialize v_map
			v_map = DwellTimeChecker.Map()

			# Initial value of location raw, dwell time, dwell average
			value = (0, 0), 0, 0

			# Identify all location then save them to v_map
			y = constant.Y_MIN
			while y <= y_max:
				x = constant.X_MIN
				while x <= x_max:

					# Save identified location to v_map
					location = x, y
					v_map.add_to_map(location,value)

					x = x + constant.MOVE_CNT
				y = y + constant.MOVE_CNT

			return v_map

		# function __get_corners
		# Description: Function to get corner location neighbors
		# Paremeter: None
		# Return value: None
		def __get_corners(self):
			"""Initialize corner location neighbors"""
			
			# Top left
			location = constant.X_MIN, constant.Y_MIN
			x, y = location

			# Neighbor list
			neighbors = []
			neighbors.append(self.__get_n_right(x,y))
			neighbors.append(self.__get_n_bottom_mid(x,y))
			neighbors.append(self.__get_n_bottom_right(x,y))

			# Record neighbors
			self.__corners.add_to_map(location, neighbors)

			# Top Right
			location = constant.X_MAX, constant.Y_MIN
			x, y = location

			# Neighbor list
			neighbors = []
			neighbors.append(self.__get_n_left(x,y))
			neighbors.append(self.__get_n_bottom_mid(x,y))
			neighbors.append(self.__get_n_bottom_left(x,y))

			# Record neighbors
			self.__corners.add_to_map(location, neighbors)

			# Bottom Left
			location = constant.X_MIN, constant.Y_MAX
			x, y = location

			# Neighbor list
			neighbors = []
			neighbors.append(self.__get_n_right(x,y))
			neighbors.append(self.__get_n_top_mid(x,y))
			neighbors.append(self.__get_n_top_right(x,y))

			# Record neighbors
			self.__corners.add_to_map(location, neighbors)

			# Bottom Right
			location = constant.X_MAX, constant.Y_MAX
			x, y = location

			# Neighbor list
			neighbors = []
			neighbors.append(self.__get_n_left(x,y))
			neighbors.append(self.__get_n_top_mid(x,y))
			neighbors.append(self.__get_n_top_left(x,y))

			# Record neighbors
			self.__corners.add_to_map(location, neighbors)

		# function __get_sides
		# Description: Function to get side location neighbors
		# Paremeter: None
		# Return value: None
		def __get_sides(self):
			"""Initialize side location neighbors"""
			
			# Skip corners
			y = constant.Y_MIN + constant.MOVE_CNT
			y_max = constant.Y_MAX - constant.MOVE_CNT

			# Check left and right sides position except corners
			while y <= y_max:

				# Neighbor list
				neighbors = []

				# Left side
				x = constant.X_MIN
				location = x, y
				# Left side neighbors
				neighbors.append(self.__get_n_right(x,y))
				neighbors.append(self.__get_n_top_mid(x,y))
				neighbors.append(self.__get_n_top_right(x,y))
				neighbors.append(self.__get_n_bottom_mid(x,y))
				neighbors.append(self.__get_n_bottom_right(x,y))

				# Record neighbors
				self.__sides.add_to_map(location, neighbors)

				# Neighbor list
				neighbors = []

				# Right side
				x = constant.X_MAX
				location = x, y
				# Right side neighbors
				neighbors.append(self.__get_n_left(x,y))
				neighbors.append(self.__get_n_top_mid(x,y))
				neighbors.append(self.__get_n_top_left(x,y))
				neighbors.append(self.__get_n_bottom_mid(x,y))
				neighbors.append(self.__get_n_bottom_left(x,y))

				# Record neighbors
				self.__sides.add_to_map(location, neighbors)

				y = y + constant.MOVE_CNT

			# Skip corners
			x = constant.X_MIN + constant.MOVE_CNT
			x_max = constant.X_MAX - constant.MOVE_CNT

			# Check top and bottom sides position except corners
			while x <= x_max:

				# Neighbor list
				neighbors = []
				
				# Top side
				y = constant.Y_MIN
				location = x, y
				# Top side neighbors
				neighbors.append(self.__get_n_left(x,y))
				neighbors.append(self.__get_n_right(x,y))
				neighbors.append(self.__get_n_bottom_left(x,y))
				neighbors.append(self.__get_n_bottom_mid(x,y))
				neighbors.append(self.__get_n_bottom_right(x,y))

				# Record neighbors
				self.__sides.add_to_map(location, neighbors)

				# Neighbor list
				neighbors = []

				# Bottom side
				y = constant.Y_MAX
				location = x, y
				# Bottom side neighbors
				neighbors.append(self.__get_n_left(x,y))
				neighbors.append(self.__get_n_right(x,y))
				neighbors.append(self.__get_n_top_left(x,y))
				neighbors.append(self.__get_n_top_mid(x,y))
				neighbors.append(self.__get_n_top_right(x,y))

				# Record neighbors
				self.__sides.add_to_map(location, neighbors)

				x = x + constant.MOVE_CNT

		# function __get_insides
		# Description: Function to get inside location neighbors
		# Paremeter: None
		# Return value: None
		def __get_insides(self):
			"""Initialize inside location neighbors"""

			# Skip corners and sides
			
			y_max = constant.Y_MAX - constant.MOVE_CNT
			x_max = constant.X_MAX - constant.MOVE_CNT

			# Compute average for insides
			y = constant.Y_MIN + constant.MOVE_CNT
			while y <= y_max:
				x = constant.X_MIN + constant.MOVE_CNT
				while x <= x_max:

					# Target location
					location = x, y

					# neighbor list
					neighbors = []
					
					# All neighbors
					neighbors.append(self.__get_n_left(x,y))
					neighbors.append(self.__get_n_right(x,y))
					neighbors.append(self.__get_n_top_left(x,y))
					neighbors.append(self.__get_n_top_mid(x,y))
					neighbors.append(self.__get_n_top_right(x,y))
					neighbors.append(self.__get_n_bottom_left(x,y))
					neighbors.append(self.__get_n_bottom_mid(x,y))
					neighbors.append(self.__get_n_bottom_right(x,y))

					# Record neighbors
					self.__insides.add_to_map(location, neighbors)

					x = x + constant.MOVE_CNT
				y = y + constant.MOVE_CNT


		# function __get_n_top_left
		# Description: Function to get top-left cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_top_left(self, x, y):
			"""Get top-left cube neighbor"""
			location = x - constant.MOVE_CNT, y - constant.MOVE_CNT
			return location

		# function __get_n_top_mid
		# Description: Function to get top-mid cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_top_mid(self, x, y):
			"""Get top-mid cube neighbor"""
			location = x, y - constant.MOVE_CNT
			return location

		# function __get_n_top_right
		# Description: Function to get top-right cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_top_right(self, x, y):
			"""Get top-right cube neighbor"""
			location = x + constant.MOVE_CNT, y - constant.MOVE_CNT
			return location

		# function __get_n_left
		# Description: Function to get left cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_left(self, x, y):
			"""Get left cube neighbor"""
			location = x - constant.MOVE_CNT, y
			return location

		# function __get_n_right
		# Description: Function to get right cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_right(self, x, y):
			"""Get right cube neighbor"""
			location = x + constant.MOVE_CNT, y
			return location

		# function __get_n_bottom_left
		# Description: Function to get bottom-left cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_bottom_left(self, x, y):
			"""Get bottom-left cube neighbor"""
			location = x - constant.MOVE_CNT, y + constant.MOVE_CNT
			return location

		# function __get_n_bottom_mid
		# Description: Function to get bottom-mid cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_bottom_mid(self, x, y):
			"""Get bottom-mid cube neighbor"""
			location = x, y + constant.MOVE_CNT
			return location

		# function __get_n_bottom_right
		# Description: Function to get bottom-right cube neighbor
		# Paremeter: x, y
		# Return value: location
		def __get_n_bottom_right(self, x, y):
			"""Get bottom-right cube neighbor"""
			location = x + constant.MOVE_CNT, y + constant.MOVE_CNT
			return location

		# function __compute
		# Description: Function to compute average of location in category map
		# Paremeter: track_id, v_map, category_map, cube_cnt
		# Return value: None
		def __compute(self, track_id, v_map, category_map, cube_cnt):
			"""Compute dwell time average within the category map"""

			# Category map: __corners, __sides, __insides
			# Check every location
			for loc_trans in category_map.keys():

				loc_raw, dwell_time, _ = v_map[loc_trans]		# Get location dwell time
				total_dt = dwell_time 				# Holds total dwell time

				# Check neighbors
				for n in category_map[loc_trans]:

					# Get neighbor dwell time
					_, n_dt, _ = v_map[n]
					# Add neighbor dwell time		
					total_dt = total_dt + n_dt

				# Get average of a corner with neighbors. Round-off is applied.
				dwell_average = int((total_dt / cube_cnt) + 0.5)

				# Set average of current location
				v_map[loc_trans] = loc_raw, dwell_time, dwell_average

				# Check if the average dwell time reached the threshold
				if self.__conf_dwell_time_average <= dwell_average:

					# Add track id to the alert list
					self.__alert_id_list.append(track_id)
					
					# date and time with timezone
					dt_now = datetime.now(tz=timezone.utc)
					time_now = dt_now.strftime(constant.TIME_STAMP_STR)

					# Add alert to message manager
					self.__message_manager.add(track_id, time_now, loc_raw)

					break


		# function compute_average
		# Description: Function that trigger to compute the dwell time average in all location
		# Paremeter: None
		# Return value: None
		def compute_average(self):

			# Check every track id
			for track_id in self.keys():

				# Skip if the track id has alert
				if track_id in self.__alert_id_list:
					continue

				# Get v_map of track id
				v_map = self[track_id]

				# Compute corners
				self.__compute(track_id, v_map, self.__corners, constant.CORNER_CUBE_CNT)
				
				# Compute sides
				self.__compute(track_id, v_map, self.__sides, constant.SIDE_CUBE_CNT)

				# Compute insides
				self.__compute(track_id, v_map, self.__insides, constant.IN_CUBE_CNT)

		# function get_alert_list
		# Description: Function to return the alert list from TrackMap
		# Paremeter: None
		# Return value: __alert_id_list
		def get_alert_list(self):
			"""Function that returns the alert id list"""

			return self.__alert_id_list

		# function remove_alert_from_list
		# Description: Function to remove track id from alert list in TrackMap
		# Paremeter: None
		# Return value: None
		def remove_alert_from_list(self, track_id):
			"""Remove track id from aler list here in TrackMap"""
			self.__alert_id_list.remove(track_id)

		


















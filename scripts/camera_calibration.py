#!/usr/bin/env python3

#pylint: disable=wrong-import-position
import cv2
import numpy as np

# class Calibration
# Description: Camera view calibration
# Paremeter: None
# Return value: None
class Calibration:

	__calibration = None	# Holds the Calibration class instance

	# function __init__()
	# Description: Class constructor
	# Paremeter: None
	# Return value: __calibration
	def __init__(self):
		"""Class constructor"""

		# Check if calibration is none
		if self.__calibration is None:
			
			# Get calibration instance
			self.__calibration = super().__init__();

		return self.__calibration

	# function draw_frame()
	# Description: Function to draw frame for calibration guidelines.
	# 			   After calibration, draw frame with the plotted points and lines
	# Paremeter: None
	# Return value: frame
	def draw_frame(self, frame, center_points):
	    """Return frame with plotted points and lines"""

	    for center in center_points:
	        cv2.circle(frame, center, 5, (255, 0, 255), -1) #characteristic of the points
	    #characteristics of lines drawn in the view
	    cv2.line(frame, center_points[0], center_points[1], (255, 255, 255), 2)
	    cv2.line(frame, center_points[1], center_points[3], (255, 255, 255), 2)
	    cv2.line(frame, center_points[0], center_points[2], (255, 255, 255), 2)
	    cv2.line(frame, center_points[3], center_points[2], (255, 255, 255), 2)
	    return frame

	# function get_2d_point()
	# Description: Function to get the coordinates of the detected object
	# Paremeter: centroid, points1, points2
	# Return value: new_x, new_y
	def get_2d_point(self, centroid, points1, points2):
	    """Get x and y coordinates that will be used in tracker module"""
	    #################################################
	    # compute point in 2D map
	    # calculate matrix Homo
	    homo, status = cv2.findHomography(points1, points2)
	    axis = np.array([centroid], dtype='float32') # provide a point you wish to map
	    axis = np.array([axis])
	    points_out = cv2.perspectiveTransform(axis, homo) # finally, get the mapping
	    new_x = points_out[0][0][0] #points at the warped image
	    new_y = points_out[0][0][1] #points at the warped image
	    return new_x, new_y


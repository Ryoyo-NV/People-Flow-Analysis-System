#!/usr/bin/env python3

################################################################################
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

#pylint: disable=wrong-import-position
import sys
import os
from os import path
sys.path.append('../')
import platform
import configparser
from threading import Thread
import time
import math
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
import cv2
import numpy as np
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call
import camera_calibration as cc
import dwell_time_checker as dt
import message_manager as mm
import pyds
import constant

from sort import *
import json

class Tracker(cc.Calibration):
#class Tracker(cc.Calibration):

    __func_name = "Tracker"
    __tracker = None
    __display = None

    __fps_streams = {}
    __frame_number = 0
    __saved_count = {}
    __frame_image = None
    __black = None
    __img = None
    __output_img = None
    __pipeline = None
    __id_loc_buffer = []            # Holds raw location and id
    __old_id_loc_buffer = []        # Holds previous location and id for filtering
    __id_grid_loc_buffer = []       # Buffer for dwell time. It holds grid location and id
    __cntr = 0

    __reset_alert_flag = False      # When mouse left-button is double clicked,
                                    # this flag will turn on
    __reset_alert_coor = None       # When mouse left-button is double clicked,
                                    # x and y are saved here as coordinates

    __old_epoch = 0                 # Old epoch to check timing per second

    __track_bounding_boxes = []

    __dwell_time_checker = None      # Holds the instance of class DwellTimeChecker
    __message_manager = None         # Holds the instance of class MessageManager
    __obj_confidence = []            # Holds detected object confidence per frame
    __names = []                     # Holds list of name per frame
    __bounding_boxes = []            # Holds list of bounding boxes per frame

    # define image variables for display
    __pts1 = None                    # points 1, hold mouse-clicked points
    __pts2 = None                    # points 2, hold points with from variable aspect ratio
    __corner_pts = None              # corner points coordinate
    __corner_point_index = 0         # corner points index
    __cx = 0                         # centroid x data 
    __cy = 0                         # centroid y data
    __cx_2d = 0                      # 2d x data
    __cy_2d = 0                      # 2d y data
    __calibrated_flag = False        # flag to know if calibration process is already executed
 
    __image_flag = []                # When image need to be saved

    __pgie_classes_str = ["Person", "Bag", "Face"]
    __sort_tracker = Sort()          # create SORT object

    def __init__(self, message_manager):
        if self.__tracker is None:
            self.__tracker = super().__init__()

            # Set user configuration class instance
            config = message_manager.getUserConfig()

            self.__conf_ar_width = config.get_ar_width()     # Set aspect ratio width from user config
            self.__conf_ar_height = config.get_ar_height()   # Set aspect ratio height from user config
            self.__conf_ar = config.get_aspect_ratio()       # Set aspect ratio from user config
            self.__conf_px_per_ft = config.get_px_per_ft()   # Set pixel per feet from user config
            self.__conf_cam_mode = config.get_cam_mode()     # Set camera mode from user config

            self.__frame_image = np.zeros((constant.MUXER_OUTPUT_HEIGHT, constant.TILED_OUTPUT_WIDTH, 3), np.uint8)
            self.__black = np.zeros((self.__conf_ar_height, self.__conf_ar_width, 3), np.uint8)
            self.__img = np.zeros((self.__conf_ar_height, self.__conf_ar_width, 3), np.uint8)
            self.__output_img = np.zeros((self.__conf_ar_height, self.__conf_ar_width, 3), np.uint8)
            #self.__display = display
            cc.Calibration.__init__(self)
            self.__dwell_time_checker = dt.DwellTimeChecker(message_manager)
            self.__message_manager = message_manager
            # define points 2
            self.__pts2 = np.float32([[0, 0], \
                [self.__conf_ar[1], 0], \
                [0, self.__conf_ar[0]], \
                [self.__conf_ar[1], \
                self.__conf_ar[0]]])

            # corner points coordinate
            self.__corner_pts = [(0, 0), (0, 0), (0, 0), (0, 0)]

        return self.__tracker

    def run(self):
        print(self.__func_name)

    # tiler_sink_pad_buffer_probe  will extract metadata received on tiler src pad
    # and update params for drawing rectangle, object information etc.
    def __tiler_sink_pad_buffer_probe(self, pad, info, u_data):
        frame_number = 0
        num_rects = 0
        obj_counter = {
            constant.PGIE_CLASS_ID_PERSON:0,
            constant.PGIE_CLASS_ID_BAG:0,
            constant.PGIE_CLASS_ID_FACE:0
            }
        gst_buffer = info.get_buffer()
        if not gst_buffer:
            print("Unable to get GstBuffer ")
            return

        image_save_time = False     # Timing to save image

        # Retrieve batch metadata from the gst_buffer
        # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))

        l_frame = batch_meta.frame_meta_list
        self.black = np.zeros((self.__conf_ar_height, self.__conf_ar_width, 3), np.uint8)
        self.black = self.draw_grid(self.black, self.__conf_px_per_ft)
        while l_frame is not None:
            try:
                # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
                # The casting is done by pyds.NvDsFrameMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone.
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break
            #global frame counter
            self.__cntr += 1
            # clear ID and location buffer for new frame
            self.__id_loc_buffer = []
            l_obj = frame_meta.obj_meta_list
            num_rects = frame_meta.num_obj_meta
            is_first_obj = True
            save_image = False
            while l_obj is not None:
                try:
                    # Casting l_obj.data to pyds.NvDsObjectMeta
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                obj_counter[obj_meta.class_id] += 1
                # Periodically check for objects with borderline confidence value that may be false positive detections.
                # If such detections are found, annoate the frame with bboxes and confidence value.
                # Save the annotated frame to file.
                if is_first_obj:
                    is_first_obj = False
                    # Getting Image data using nvbufsurface
                    # the input should be address of buffer and batch_id
                    n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
                    #convert python array into numy array format.
                    self.__frame_image = np.array(n_frame, copy=True, order='C')
                    #covert the array into cv2 default color format
                    self.__frame_image = cv2.cvtColor(self.__frame_image, cv2.COLOR_RGBA2BGRA)
                    self.__img = cv2.cvtColor(self.__frame_image, cv2.COLOR_BGRA2BGR)
                save_image = True
                if obj_meta.class_id == constant.PGIE_CLASS_ID_PERSON:
                    self.__append_object(obj_meta, obj_meta.confidence)
                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break

            # Write connection status
            self.__check_connection_status()

            if self.__calibrated_flag:
                self.__img = self.draw_grid_in_cam(self.__img, self.__conf_px_per_ft)

            # process only if bounding box has value
            track_bbs_ids = []
            if 0 < len(self.__bounding_boxes):

                track_bbs_ids = self.__sort_tracker.update(np.array(self.__bounding_boxes))

            tb = time.time()

            # Process each tracked object
            for tracked_bbox_id in track_bbs_ids:
                bbox = tracked_bbox_id[:4]
                class_name = "Person"
                track_id = tracked_bbox_id[4]

                # Reset alert of a track id
                self.__reset_alert(track_id, int(bbox[0]), int(bbox[1]),\
                     int(bbox[2]), int(bbox[3]))

                # Check if an object has alert from dwell time checker
                alert_on_flag = self.__dwell_time_checker.get_alert_flag(track_id)
                if not alert_on_flag:
                    color = (50, 200, 0)
                # Change bounding box color into red if alert flag is True
                else:

                    # Check if track id is not yet included in image flag
                    if track_id not in self.__image_flag:
                        # Turn on timing to notify message manager for the image to be saved
                        image_save_time = True
                        # Add track id
                        self.__image_flag.append(str(track_id))

                    color = (0, 0, 200)
                # Draw bounding box
                cv2.rectangle(self.__img, (int(bbox[0]), int(bbox[1])),\
                 (int(bbox[2]), int(bbox[3])), color, 1)
                cv2.putText(self.__img, str(int(track_id)),\
                 (int(bbox[0]), int(bbox[1]-10)), 0, 0.5, (255, 255, 255), 1)
                #check if old buffer has value
                if self.__old_id_loc_buffer is not []:
                    # flag to check if detected object is previously existing
                    found = False
                    # check every id and position
                    for i in self.__old_id_loc_buffer:
                        # check if object's id existed from previous frame print(i[0])
                        if i[0] == track_id:
                            # set flag
                            found = True
                            # get average as filter for sudden movement
                            self.__cx = int((bbox[0] + (bbox[2] - bbox[0])/2) * 0.3 + i[1] * 0.7)
                            self.__cy = int((bbox[1] + (bbox[3] - bbox[1])) * 0.3 + i[2] * 0.7)
                    if found == False:
                        # if not found, it means it is a new object, get it's initial position
                        self.__cx = int(bbox[0] + (bbox[2] - bbox[0])/2)
                        self.__cy = int(bbox[1] + (bbox[3] - bbox[1]))
                # draw the point
                cv2.circle(self.__img, (self.__cx, self.__cy), 7, (255, 0, 0), -1)
                # update buffer
                self.__id_loc_buffer.append((track_id, self.__cx, self.__cy))
                # draw the points on 2d map
                self.__black = self.draw_2d_points(self.black, track_id)
            # Store current buffer for next frame processing
            self.__old_id_loc_buffer = self.__id_loc_buffer

            # Get final processing image for display
            self.__output_img = self.__img

            # Clear for next frame tracker processing
            self.__bounding_boxes = []

            # Clear reset alert flag
            # This is set just in case reset alert failed or no matching coordinates
            self.__reset_alert_flag = False

            # Check if timing to notify message manager for image to be saved
            if image_save_time:

                # Turn off flag
                image_save_time = False

                # Convert frame image to byteArray
                is_success, img_buffer = cv2.imencode(".jpg", self.__img)
                byte_img = img_buffer.tobytes()

                # Set image to Message Manager for alert
                self.__message_manager.set_image(byte_img)

            # Save image
            if save_image:
                cv2.imwrite(constant.DIR_NAME+"/frame_"+str(0)+".jpg", self.__output_img)

            # Check if calibration is done
            # Check if its time to pass data to dwell time checker
            if self.__calibrated_flag and self.__is_pass_data_time():
                # Send tracking data to dwell time checker
                self.__dwell_time_checker.input(self.__id_grid_loc_buffer)
                self.__id_grid_loc_buffer.clear()
                print("FRAME " + str(self.__cntr) + "===============")
            try:
                l_frame = l_frame.next
            except StopIteration:
                break
        return Gst.PadProbeReturn.OK

    #Function name: __append_object
    #Desription: List important info from each object in a frame for deepsort tracker
    #Parameter: object meta and confidence
    #Return: None
    def __append_object(self, obj_meta, confidence):
        """List important info from each object in a frame for deepsort tracker"""
        confidence = '{0:.2f}'.format(confidence)
        rect_params = obj_meta.rect_params
        top = int(rect_params.top)
        left = int(rect_params.left)
        width = int(rect_params.width)
        height = int(rect_params.height)
        self.__bounding_boxes.append([left, top, left+width, top+height])

    #Function name: draw_2d_points
    #Desription: Draw 2d map and points
    #Parameter: image, tracked_id
    #Return: image
    def draw_2d_points(self, image, tracked_id):
        """Draw filled circle on detected object in black 2d space"""
        if self.__corner_point_index >= 4:
            grid_coor_raw, grid_coor_trans = self.get_loc()
            self.__id_grid_loc_buffer.append((tracked_id, grid_coor_raw, grid_coor_trans))

            # Compute bird's eye coordinates
            b_eye_x = int(self.__cx_2d - (self.__cx_2d % self.__conf_px_per_ft))
            b_eye_y = int(self.__cy_2d - (self.__cy_2d % self.__conf_px_per_ft))

            cv2.putText(image, str(tracked_id),\
                (int(b_eye_x-10), int(b_eye_y-10)),\
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Fill-in the bird's eye box where a detected person is currently located
            pt1 = b_eye_x, b_eye_y
            pt2 = (int(pt1[0] + self.__conf_px_per_ft), int(pt1[1] + self.__conf_px_per_ft))
            pt_color = (255, 255, 0)
            cv2.rectangle(image, pt1, pt2, pt_color, -1)

            # draw a circle indicates the location of a detected person in the bird's eye view
            cv2.circle(image, (self.__cx_2d, self.__cy_2d), 10, (255, 255, 255), -1)
        return image

    #Function name: get_loc
    #Desription: Convert raw to grid position
    #Parameter: None
    #Return: grid_coor_raw, grid_coor_trans
    def get_loc(self):
        """Convert raw to grid position"""
        if self.__corner_point_index >= 4:
            self.__pts1 = np.float32([\
            [self.__corner_pts[0][0], self.__corner_pts[0][1]],\
            [self.__corner_pts[1][0], self.__corner_pts[1][1]],\
            [self.__corner_pts[2][0], self.__corner_pts[2][1]],\
            [self.__corner_pts[3][0], self.__corner_pts[3][1]]])
            self.__cx_2d, self.__cy_2d = self.get_2d_point((self.__cx, self.__cy),\
             self.__pts1, self.__pts2)

            grid_coor_trans = self.get_grid_position((self.__cx_2d, self.__cy_2d),\
             self.__conf_px_per_ft)
            grid_coor_raw = self.__cx, self.__cy

            return grid_coor_raw, grid_coor_trans

        else:
            return []

    #Function name: draw_grid
    #Desription: Draw grid lines in 2D view
    #Parameter: image, pixel_per_unit
    #Return: image
    def draw_grid(self, image, pixel_per_unit):
        """Draw grid lines in 2D view"""
        row = int(self.__conf_ar_height / pixel_per_unit)
        column = int(self.__conf_ar_width / pixel_per_unit)
        for r in range(row + 1):
            y = r * pixel_per_unit
            cv2.line(image, (0, y), (self.__conf_ar_width, y), (255, 255, 255), 1)
        for c in range(column + 1):
            x = c * pixel_per_unit
            cv2.line(image, (x, 0), (x, self.__conf_ar_height), (255, 255, 255), 1)
        return image
    
    #Function name: draw_grid_in_cam
    #Desription: Draw dot grid in camera view
    #Parameter: image, pixel_per_unit
    #Return: image
    def draw_grid_in_cam(self, image, pixel_per_unit):
        """Draw dot grid in camera view"""
        row = int(self.__conf_ar_height / pixel_per_unit)
        column = int(self.__conf_ar_width / pixel_per_unit)
        # get intersection points of grid
        for r in range(row + 1):
            y = r * pixel_per_unit
            for c in range(column + 1):
                x = c * pixel_per_unit
                color = (int(x*0.8), int(y*0.8), 0)
                # draw the intersection dot in 2d view
                cv2.circle(self.black, (x,y), 3, color, -1)
                # transform the intersection dot
                if self.__pts1 is not None and self.__pts2 is not None:
                        cam_x, cam_y = self.get_2d_point((x, y), self.__pts2, self.__pts1)
                        # draw the intersection dot in camera view
                        cv2.circle(image, (cam_x, cam_y), 2, color, -1)
        return image

    #Function name: get_grid_position
    #Desription: Get grid coordinate
    #Parameter: position, pixel_per_unit
    #Return: grid_x,grid_y
    def get_grid_position(self, position, pixel_per_unit):
        """Get grid coordinate"""
        grid_y = int((position[1] / pixel_per_unit) + 0.50)
        grid_x = int((position[0] / pixel_per_unit) + 0.50)
        return grid_x, grid_y

    #Function name: get_points
    #Desription: Get calibration points
    #Parameter: event, x, y, flags, param
    #Return: True
    def get_points(self, event, x, y, flags, param):
        """Mouse-click callback to get 4 points"""
        if event == cv2.EVENT_LBUTTONDBLCLK:
            if self.__corner_point_index < 4:
                self.__corner_pts[self.__corner_point_index] = (x, y)
                self.__corner_point_index = self.__corner_point_index + 1
                if self.__corner_point_index >= 4:
                    self.__calibrated_flag = True
            else:
                # Set coordinates for alert reset
                self.__reset_alert_coor = x, y
                # Set alert reset flag to True
                self.__reset_alert_flag = True
       
    #Function name: get_img_show_vars
    #Desription: Get necessary variables for display
    #Parameter: None
    #Return: __output_img, __black, __corner_pts, __cx, __cy, __corner_point_index
    def get_img_show_vars(self):
        """return variable for streaming"""
        return self.__output_img,\
            self.__black,\
            self.__corner_pts,\
            self.__cx,\
            self.__cy,\
            self.__corner_point_index

    #Function name: image_show
    #Desription: Display streams
    #Parameter: pipeline
    #Return: None
    def image_show(self, pipeline):
        """Display streams"""
        cv2.namedWindow('Frame')
        cv2.setMouseCallback('Frame', self.get_points)
        while True:
            frame_image, black, corner_pts, cx, cy, corner_point_index = self.get_img_show_vars()
            if self.__calibrated_flag:
                self.__pts1 = np.float32([\
                [corner_pts[0][0], corner_pts[0][1]],\
                [corner_pts[1][0], corner_pts[1][1]],\
                [corner_pts[2][0], corner_pts[2][1]],\
                [corner_pts[3][0], corner_pts[3][1]]])
                cv2.imshow('Black', black)

            # display guide line during calibration process
            frame_image = self.draw_frame(frame_image, corner_pts)

            # display the detection and trackng video window
            cv2.imshow('Frame', frame_image)

            # get user input keys
            key = cv2.waitKey(20)
            if key & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        pipeline.set_state(Gst.State.NULL)
        os._exit(0)

    #Function name: __reset_alert
    #Desription: Reset alert of a track id
    #Parameter: track_id, x1, x2, y1, y2
    #Return: None
    def __reset_alert(self, track_id, x1, y1, x2, y2):

        # If reset flag is true, reset alert track id
        if self.__reset_alert_flag is True:
            # get coordinates for reset
            x, y = self.__reset_alert_coor

            # check if reset coordinates are in range of alerted track id
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:

                # Run remove alert from DwellTimeChecker and get result
                result = self.__dwell_time_checker.remove_alert(track_id)

                if constant.RETURN_OK == result:

                    print("Reset Alert success!")
                    # Turn off reset flag
                    self.__reset_alert_flag = False
                    # Remove track id from image flag list
                    self.__image_flag.remove(str(track_id))
                    # Clear reset coordinates
                    self.__reset_alert_coor = (0, 0)

                else:
                    print("Reset Alert failed. Please try again...")

    #Function name: __check_connection_status
    #Desription: Function that put the connection status on the screen
    #Parameter: None
    #Return: None
    def __check_connection_status(self):
        """Display connection status on the screen"""

        message = None
        bg_pt2 = None

        # Do nothing if not yet calibrated
        if not self.__calibrated_flag:
            return

        is_iothub_ok = self.__message_manager.is_iothub_conn_ok()   # Iothub connection status
        is_mobile_ok = self.__message_manager.is_mobile_conn_ok()   # Mobile connection status

        # Check if iothub and mobile connections are ok
        if is_iothub_ok and is_mobile_ok:
            return
        elif not is_iothub_ok and not is_mobile_ok:
            bg_pt2 = constant.CONN_STAT_BG_PT2
        else:
            bg_pt2 = constant.CONN_STAT_BG_PT3

        # draw background
        cv2.rectangle(self.__img, constant.CONN_STAT_BG_PT1, bg_pt2,\
            constant.CONN_STAT_BG_COLOR, -1)

        # Check if iothub connection is ok
        if not is_iothub_ok:
            message = "IoT hub connection status: Error"

            # Show on the screen the IOT hub connection status
            cv2.putText(self.__img, message, constant.CONN_STAT_IOT_PT,\
                cv2.FONT_HERSHEY_SIMPLEX, constant.CONN_STAT_FONT_SIZE, constant.CONN_STAT_FONT_COLOR, 1)

        # Check if mobile connection is ok
        if not is_mobile_ok:
            message = "Mobile connection status: Error"

            if is_iothub_ok:
                pt = constant.CONN_STAT_IOT_PT
            else:
                pt = constant.CONN_STAT_MOB_PT

            # Show on the screen the IOT hub connection status
            cv2.putText(self.__img, message, pt,\
                cv2.FONT_HERSHEY_SIMPLEX, constant.CONN_STAT_FONT_SIZE, constant.CONN_STAT_FONT_COLOR, 1)


    #Function name: __is_pass_data_time
    #Desription: Function that returns the flag for pass data timing
    #Parameter: None
    #Return: True, False
    def __is_pass_data_time(self):

        time_now = time.time()      # Get the current time
        result = False              # Holds the value for function return

        # Check if old epoch has no old value
        if self.__old_epoch is 0:

            # Send time now to old epoch
            self.__old_epoch = time_now

        else:

            # Get time difference of old time vs new time
            diff = time_now - self.__old_epoch

            # Check if it is the time to pass data to MessageManager
            # Check if diff is negative due to wrap around value of time_now
            if constant.PASS_DATA_TIMING <= diff or 0 > diff:

                # Change old epoch with the current time
                self.__old_epoch = time_now

                # Pass data timing
                result = True

        return result


    def start_tracker(self, args):
        """Deepstream function for detection and tracking"""
        # Check input arguments
        if len(args) < 2:
            live_camera = True
            stream_path = "/dev/video0"
        elif len(args) >= 2:
            live_camera = False
            stream_path = args[1]
        #stream_path = "/home/awsol/Downloads/topview_many_people_detected.mp4"

        number_sources = 1
        # Standard GStreamer initialization
        GObject.threads_init()
        Gst.init(None)
        # Create gstreamer elements
        # Create Pipeline element that will form a connection of other elements
        print("Creating Pipeline \n ")
        self.__pipeline = Gst.Pipeline()

        if not self.__pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")
            return False
        if live_camera:
            if constant.RPI_CAM_MODE == self.__conf_cam_mode:
                print("Creating Source \n ")
                source = Gst.ElementFactory.make("nvarguscamerasrc", "src-elem")
                if not source:
                    sys.stderr.write(" Unable to create Source \n")
                    return False
            else:
                print("Creating Source \n ")
                source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
                if not source:
                    sys.stderr.write(" Unable to create Source \n")
                    return False

                caps_v4l2src = Gst.ElementFactory.make("capsfilter", "v4l2src_caps")
                if not caps_v4l2src:
                    sys.stderr.write(" Unable to create v4l2src capsfilter \n")
                    return False
                print("Creating Video Converter \n")
                # videoconvert to make sure a superset of raw formats are supported
                vidconvsrc = Gst.ElementFactory.make("videoconvert", "convertor_src1")
                if not vidconvsrc:
                    sys.stderr.write(" Unable to create videoconvert \n")
                    return False
            # nvvideoconvert to convert incoming raw buffers to NVMM Mem (NvBufSurface API)
            nvvidconvsrc = Gst.ElementFactory.make("nvvideoconvert", "convertor_src2")
            if not nvvidconvsrc:
                sys.stderr.write(" Unable to create Nvvideoconvert \n")
                return False
            caps_vidconvsrc = Gst.ElementFactory.make("capsfilter", "nvmm_caps")
            if not caps_vidconvsrc:
                sys.stderr.write(" Unable to create capsfilter \n")
                return False
        else:
            # Source element for reading from the file
            print("Creating Source \n ")
            source = Gst.ElementFactory.make("filesrc", "file-source")
            if not source:
                sys.stderr.write(" Unable to create Source \n")
                return False
            # Since the data format in the input file is elementary h264 stream,
            # we need a h264parser
            print("Creating H264Parser \n")
            h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
            if not h264parser:
                sys.stderr.write(" Unable to create h264 parser \n")
                return False
            # Use nvdec_h264 for hardware accelerated decode on GPU
            print("Creating Decoder \n")
            decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
            if not decoder:
                sys.stderr.write(" Unable to create Nvv4l2 Decoder \n")
                return False
        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")
            return False
        # Use nvinfer to run inferencing on decoder's output,
        # behaviour of inferencing is set through config file
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            sys.stderr.write(" Unable to create pgie \n")
            return False
        # Add nvvidconv1 and filter1 to convert the frames to RGBA
        # which is easier to work with in Python.
        print("Creating nvvidconv1 \n ")
        nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
        if not nvvidconv1:
            sys.stderr.write(" Unable to create nvvidconv1 \n")
            return False
        print("Creating filter1 \n ")
        caps1 = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
        filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
        if not filter1:
            sys.stderr.write(" Unable to get the caps filter1 \n")
            return False
        #filter1.set_property("caps", caps1)
        print("Creating tiler \n ")
        tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
        if not tiler:
            sys.stderr.write(" Unable to create tiler \n")
            return False
        print("Creating nvvidconv \n ")
        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
        if not nvvidconv:
            sys.stderr.write(" Unable to create nvvidconv \n")
            return False
        print("Creating nvosd \n ")
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")
            return False
        print("Creating Fake sink \n")
        # sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
        sink = Gst.ElementFactory.make("fakesink", "fakesink")
        if not sink:
            sys.stderr.write(" Unable to create fake sink \n")
            return False
        print("Playing file %s " %stream_path)
        if live_camera:
            if constant.RPI_CAM_MODE == self.__conf_cam_mode:
                source.set_property('bufapi-version', True)
            else:
                source.set_property('device', stream_path)
                caps_v4l2src.set_property('caps', Gst.Caps.from_string("video/x-raw, framerate=30/1"))
            caps_vidconvsrc.set_property('caps', Gst.Caps.from_string("video/x-raw(memory:NVMM)"))
        else:
            source.set_property('location', stream_path)
        streammux.set_property('width', 1920)
        streammux.set_property('height', 1080)
        streammux.set_property('batch-size', 1)
        streammux.set_property('batched-push-timeout', 4000000)

        tiler_rows = int(math.sqrt(number_sources))
        tiler_columns = int(math.ceil((1.0*number_sources)/tiler_rows))
        tiler.set_property("rows", tiler_rows)
        tiler.set_property("columns", tiler_columns)
        tiler.set_property("width", constant.TILED_OUTPUT_WIDTH)
        tiler.set_property("height", constant.TILED_OUTPUT_HEIGHT)

        sink.set_property("sync", 1)
        filter1.set_property("caps", caps1)

        if not is_aarch64():
            # Use CUDA unified memory in the pipeline so frames
            # can be easily accessed on CPU in Python.
            mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
            streammux.set_property("nvbuf-memory-type", mem_type)
            nvvidconv.set_property("nvbuf-memory-type", mem_type)
            nvvidconv1.set_property("nvbuf-memory-type", mem_type)
            tiler.set_property("nvbuf-memory-type", mem_type)

        if is_aarch64():
            sink.set_property("sync", 0)
        ########################################################################

        #Set properties of pgie
        pgie.set_property('config-file-path', constant.DSTEST2_PGIE_CONFIG)
        
        print("Adding elements to Pipeline \n")
        self.__pipeline.add(source)
        if live_camera:
            if constant.RPI_CAM_MODE != self.__conf_cam_mode:
                self.__pipeline.add(caps_v4l2src)
                self.__pipeline.add(vidconvsrc)
            self.__pipeline.add(nvvidconvsrc)
            self.__pipeline.add(caps_vidconvsrc)
        else:
            self.__pipeline.add(h264parser)
            self.__pipeline.add(decoder)
        self.__pipeline.add(streammux)
        self.__pipeline.add(pgie)
        self.__pipeline.add(tiler)
        self.__pipeline.add(nvvidconv)
        self.__pipeline.add(filter1)
        self.__pipeline.add(nvvidconv1)
        self.__pipeline.add(nvosd)
        self.__pipeline.add(sink)

        # we link the elements together
        # file-source -> h264-parser -> nvh264-decoder ->
        # nvinfer -> nvvidconv -> nvosd -> video-renderer
        print("Linking elements in the Pipeline \n")
        if live_camera:
            if constant.RPI_CAM_MODE == self.__conf_cam_mode:
                source.link(nvvidconvsrc)
            else:
                source.link(caps_v4l2src)
                caps_v4l2src.link(vidconvsrc)
                vidconvsrc.link(nvvidconvsrc)
            nvvidconvsrc.link(caps_vidconvsrc)
        else:
            source.link(h264parser)
            h264parser.link(decoder)

        sinkpad = streammux.get_request_pad("sink_0")
        if not sinkpad:
            sys.stderr.write(" Unable to get the sink pad of streammux \n")
        if live_camera:
            srcpad = caps_vidconvsrc.get_static_pad("src")
        else:
            srcpad = decoder.get_static_pad("src")
        if not srcpad:
            sys.stderr.write(" Unable to get source pad of decoder \n")
        srcpad.link(sinkpad)
        streammux.link(pgie)
        pgie.link(nvvidconv1)
        nvvidconv1.link(filter1)
        filter1.link(tiler)
        tiler.link(nvvidconv)
        nvvidconv.link(nvosd)
        nvosd.link(sink)

        # create and event loop and feed gstreamer bus mesages to it
        loop = GObject.MainLoop()

        bus = self.__pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect ("message", bus_call, loop)

        # Lets add probe to get informed of the meta data generated, we add probe to
        # the sink pad of the osd element, since by that time, the buffer would have
        # had got all the metadata.
        tiler_sink_pad = nvvidconv.get_static_pad("sink")
        if not tiler_sink_pad:
            sys.stderr.write(" Unable to get src pad \n")
        else:
            tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, self.__tiler_sink_pad_buffer_probe, 0)

        print("Starting pipeline \n")
        # start play back and listed to events
        self.__pipeline.set_state(Gst.State.PLAYING)
        #Display the Stream
        self.image_show(self.__pipeline)
        # start play back and listed to events
        try:
            loop.run()
        except:
            pass

        # cleanup
        self.__pipeline.set_state(Gst.State.NULL)

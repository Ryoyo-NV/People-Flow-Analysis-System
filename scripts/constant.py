
####################################################################################################
##################################### User Configurtion ############################################
####################################################################################################
# How to edit:
# 1. Below variables are grouped via header --> [<section name>]. e.g [display_setting]
#	 Please do not change any group header.
# 2. Every group is separated by the line of '#' for readability.
# 3. Comment above each variable indicates the purpose of it.
# 4. Please do not change any variable name. Variables are named all capital letters.
# 5. To edit the value, update the value after '=' operator. The value should be input 1 space after
#    '=' operator. Do not put any trailing after value like comment, spaces, etc.
# 6. Save the file when your done.
####################################################################################################
####################################################################################################	
####################################################################################################
# IOT Hub Client Setting
# - This group will be used for IOT Hub client connection	
#[iot_hub_client_setting]

# IOT Hub Client connection string
# - This connection string will be provided after an iot device such as jetson nano is registered in
#	Azure Cloud account.
HOST_NAME = "awsjetsonnano.azure-devices.net"
DEVICE_ID = "jetsonnano"
SHARED_ACCESS_KEY = "Ls/Ec97qmhkwAcTkz/uOy0cP+vKCO3i2dZh7YrQfBYs="

####################################################################################################
# Mobile Client Setting
# - This group will be used for Mobile client connection	
#[mobile_client_setting]

# MQTT Host (IP Address)
# - This host is the Jetson Nano's IP address that will be used for mobile client connection
HOST = "192.168.254.111"

# MQTT Port
# - This port that will be used for mobile client connection 	
PORT = 1883

####################################################################################################
# Display Setting
# - This group will be used for PFA display
#[display_setting]

# Aspect Ration (width in pixel)
# - This width is the aspect ratio of Bird's Eye view display.
AR_WIDTH = 324

# Aspect Ration (height in pixel)
# - This height is the aspect ratio of Bird's Eye view display.
AR_HEIGHT = 420

# Pixel dimension per feet
# - This dimension is used to identify 1 dwell position in Bird's Eye view display.
# - 1 dwell position is equivalent to 1 cube in Bird's Eye view display.
# - e.g. PIXEL_PER_FEET = 20, dwell position is 20x20 pixels
PIXEL_PER_FEET = 40

####################################################################################################
# Alert Setting
# - This group will be used for dwell time computation and checking for dwell time limitation	
#[alert_setting]

# Dwell Time limitation (in second)
# - This limitation is used to check if a person stay or accumulates dwell time on a single
#	position. If the person's dwell time exceeds the limit, an alert will be raised.
# - When the person has alert, his bounding box will be in color red.
# - When alert is raised, alert message will be sent to IOT Hub and mobile application.
DWELL_LIMIT = 5

# Dwell Time Average limitation
# - Dwell Time Average is computed from 1 location and its next location around.
# - Computation given:
#	--- n = neighboring location
#	--- loc = target location
#	--- ave = dwell time average
# - The computation for corners:
# 	--- ave = ((loc + n1 + n2 + n3) / 4)
# - The computation for sides:
# 	--- ave = ((loc + n1 + n2 + n3 + n4 + n5) / 6)
# - The computation for insides:
# 	--- ave = ((loc + n1 + n2 + n3 + n4 + n5 + n6 + n7 + n8) / 9)
# - e.g DWELL_TIME_AVERAGE = 0.80, the threshold is 80% of DWELL_LIMIT
# - When the average hits the threshold or higher, alert will be raised
# - When the person has alert, his bounding box will be in color red.
# - When alert is raised, alert message will be sent to IOT Hub and mobile application.
DWELL_AVERAGE_LIMIT = (DWELL_LIMIT * 0.80)

####################################################################################################	
####################################################################################################	
####################################################################################################	

# Constants for Tracker

MAX_DISPLAY_LEN=64
PGIE_CLASS_ID_PERSON = 0
PGIE_CLASS_ID_BAG = 1
PGIE_CLASS_ID_FACE = 2

# Display dimension and aspect ration
MUXER_OUTPUT_WIDTH = 1280
MUXER_OUTPUT_HEIGHT = 720
MUXER_BATCH_TIMEOUT_USEC = 4000000
TILED_OUTPUT_WIDTH = 768
TILED_OUTPUT_HEIGHT = 450

# Users input limitation
AR_WIDTH_MIN = (135*3)		# Aspect Ratio minimum width
AR_WIDTH_MAX = (200*3)		# Aspect Ratio maximum height
AR_HEIGHT_MIN = (175*3)		# Aspect Ratio minimum width
AR_HEIGHT_MAX = (276*3)		# Aspect Ratio maximum height
PX_PER_FT_MIN = 20			# Minimum pixel per feet
PX_PER_FT_MAX = 40			# Minimum pixel per feet

# Users input variable
#AR_WIDTH = 135*3
#AR_HEIGHT = 175*3
#PIXEL_PER_FEET = 20
ASPECT_RATIO = (AR_HEIGHT, AR_WIDTH)        # define aspect ratio

GST_CAPS_FEATURES_NVMM="memory:NVMM"
PGIE_CLASSES_STR= ["Person", "Bag", "Face"]

DIR_NAME = '../tmp'

DSTEST2_PGIE_CONFIG = "../config/config_infer_primary_peoplenet.txt"
#DSTEST2_PGIE_CONFIG = "../config/dstest2_pgie_config_yolo.txt"
DSTEST2_TRACKER_CONFIG = '../config/dstest2_tracker_config.txt'

#frame per second estimate
FPS_CNT = 20

# Constants for Mqtt
RETURN_OK=0
RETURN_NG=1

# Timing in second to pass track data from tracker to message_manager
PASS_DATA_TIMING = 1

# Constants for send_message.py
# The device connection string to authenticate the device with your IoT hub.
#CONNECTION_STRING = ("HostName=iothubjetsonnano.azure-devices.net;"\
#    +"DeviceId=jetsonsano;"\
#    +"SharedAccessKey=jIa9U6dq+3d7xpL+vaHrkbmkWN+PifUqeWT7mIpd6QQ=")
MESSAGE_TEXT = '{{"time": "{time_now}","id": {person_id}, \
"location": {{ "x": {location_x}, "y": {location_y} }}}}'

#HOST = "192.168.100.20"       #IP address of mqtt broker

#PORT = 1883     #default port of mqtt

MAX_CONN_TIMEOUT = 2    # Timeout to wait for iothub and mobile mqtt client connection

# Constants for Message Manager
MAX_ALERT_CNT = 100		# Maximum number of alert that can be saved when the state is busy

STATE_IDLE = 0			# State when no ongoing process
STATE_BUSY = 1			# State when there is ongoing process
STATE_ERROR = -1		# State when there is an error encountered

MAX_RETRY = 3			# Max attempt to send message to IoT hub and mobile

# Constants for Dwell time checker
X_MIN = 0											# x point left most
X_MAX = (int)(((AR_WIDTH - PIXEL_PER_FEET) / PIXEL_PER_FEET) + 0.5)	# x point right most
Y_MIN = 0											# y point top most
Y_MAX = (int)(((AR_HEIGHT - PIXEL_PER_FEET) / PIXEL_PER_FEET) + 0.5)	# y point bottom most

CORNER_CUBE_CNT = 4		# Location cube plus 3 neighboring cubes
SIDE_CUBE_CNT   = 6		# Location cube plus 5 neighboring cubes
IN_CUBE_CNT     = 9 	# Location cube plus 8 neighboring cubes

# limit of stay
#DWELL_LIMIT = 10

# location with neighbors average limit
#DWELL_AVERAGE_LIMIT = (DWELL_LIMIT * 0.80)

# x and y movement
MOVE_CNT = 1

# Time stamp format
TIME_STAMP_STR = "%Y-%m-%dT%H:%M:%S.%fZ"

###############################################################
# Components
###############################################################

# Connection status
CONN_STAT_FONT_COLOR = (225, 225, 225) 	# Connection status font color
CONN_STAT_BG_COLOR = (0, 0, 0)			# Connection status background color
CONN_STAT_IOT_PT = (5, 10)			# Connection status for iothub X and Y
CONN_STAT_MOB_PT = (5, 22)			# Connection status for mobile X and Y
CONN_STAT_BG_PT1 = (00, 00)			# Connection status background X and Y
CONN_STAT_BG_PT2 = (190, 28)		# Connection status background X + Width and Y + Height
CONN_STAT_BG_PT3 = (190, 18)		# Connection status background X + Width and Y + Height
CONN_STAT_FONT_SIZE = 0.35			# Conection status font size




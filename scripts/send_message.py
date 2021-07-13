#!/usr/bin/env python
import logging
from azure.iot.device import IoTHubDeviceClient, Message
from azure.iot.device.exceptions import CredentialError, ConnectionFailedError,\
    ConnectionDroppedError, ClientError

import paho.mqtt.client as mqtt
import config
import constant
import time

class MessageSender:

    image_path = None                   # Holds the image for mobile alert message

    def __init__(self, config):

        # Set user configurations
        self.__conf_iothub_connection_str = config.get_iot_hub_conn_string()
        self.__conf_mobile_conn_host = config.get_mobile_conn_host()
        self.__conf_mobile_conn_port = config.get_mobile_conn_port()

        # Establish mqtt client connection
        self.mobile_client = mqtt.Client()
        # Reset mqtt client state
        self.mobile_client.reinitialise()

    #function __iothub_client_init
    #Desctription: create a client from the specified connection string
    #Return value: result
    def __iothub_client_init(self):
        """create an iot hub client"""
        try:
            #create client from connection string
            client = IoTHubDeviceClient.create_from_connection_string(\
                self.__conf_iothub_connection_str)
            
        except Exception as ex:
            print("Unexpected error in connecting to client{0}".format(ex))
            logging.exception(ex)
            result = None

        else:
            result = client
        finally:
            pass

        return result

    #function iothib_client_send_message()
    #Description: function that sends message to azure hub
    #Parameter: time_now, person_id, location_x, location_y
    #Return value: None
    def iothub_client_send_message(self, time_now, person_id, location_x, location_y):
        """send message to iot hub"""

        # Create iothub client
        client = self.__iothub_client_init()

        # Check if no client is set
        if client is None:
            return constant.RETURN_NG

        try:
            # Connect to iothub
            client.connect()

            print("Connection string:", self.__conf_iothub_connection_str)

            print('time: ', time_now, ' id: ', person_id, ' location: ', location_x, location_y)
            msg_txt_formatted = constant.MESSAGE_TEXT.format(time_now=(time_now), person_id=\
                (person_id), location_x=(location_x), location_y=(location_y))
            #formatted message to be sent to iot hub
            message = Message(msg_txt_formatted)
            print(message)
            #sends message to iot hub
            client.send_message(message)

        except CredentialError as ce:
            print("Credential error in connecting to client {0}".format(ce))
            logging.exception(ce)
            print("Sending alert failed...")
            result = constant.RETURN_NG
        except ConnectionFailedError as cfe:
            print("Connection failed error in connecting to client {0}".format(cfe))
            logging.exception(cfe)
            print("Sending alert failed...")
            result = constant.RETURN_NG
        except ConnectionDroppedError as cde:
            print("Connection dropped error in connecting to client {0}".format(cde))
            logging.exception(cde)
            print("Sending alert failed...")
            result = constant.RETURN_NG
        except ClientError as clienterror:
            print("Client error in connecting to client {0}".format(clienterror))
            logging.exception(clienterror)
            print("Sending alert failed...")
            result = constant.RETURN_NG
        except:
            print("Unknown error encountered.")
            print("Sending alert failed...")
            result = constant.RETURN_NG
        else:
            print("Message successfully sent")
            result = constant.RETURN_OK
        finally:
            client.disconnect()

        return result

    #function mobile_client_send_message
    #Description: function that publishes a topic/data and message
    #Parameter: time_now, person_id, location_x, location_y
    #Return value: None
    def mobile_client_send_message(self, time_now, person_id, location_x, location_y):
        """publish a message"""

        global image_value      #holds the current frame image value in bytes

        # Mobile mqtt connection
        client = self.mobile_client

        try:
            # Timeout for image saving time
            time.sleep(0.3)

            # Connect client
            client.connect(self.__conf_mobile_conn_host,\
                self.__conf_mobile_conn_port, 60)

            ################################################################

            #publish a message
            client.publish("topic/data", str(person_id)\
                +"/"+str(time_now)+"/"+str(location_x)+"/"+str(location_y))
            print('published message!')

            #publish topic and image
            client.publish("topic/image", image_value, 0) 

        except Exception as ex:
            print("Unexpected error: {0}".format(ex))
            logging.exception(ex)
            print("Sending alert failed...")
            result = constant.RETURN_NG
        except:
            print("Sending alert failed...")
            result = constant.RETURN_NG
        else:
            print('image sent!')
            result = constant.RETURN_OK
        finally:
            #Disconnect client
            client.disconnect()

        return result

    #function set_image
    #Description: function sets the frame image value in byte form to global var
    #Parameter: image data in bytes
    #Return value: None
    def set_image(self, value):

        global image_value
        image_value = value

# People Flow Analysis System

A low-cost People Flow Analysis System developed using NVIDIA's Jetson and Deepstream SDK, integrated with high quality open source software and library.


The system is able to monitor every person within the camera vision. Each person detected will be tracked giving a unique track ID and a green bounding box will be drawn on it. When the detected person stay on the same spot for a certain duration, the system will send a message alert to an authorized Azure Iot Hub and android mobile phone. The message alert contains time, track id and location. 

There is also a calibration process to define the ground surface mapping from the camera view. The calibration input will be set by the user.

<img src="src/people_flow_analysis_demo.gif" hight="480"/>


## Prerequisite

- NVIDIA Jetson Platform
- [JetPack](https://developer.nvidia.com/embedded/jetpack) 4.4 or 4.5.x
- USB webcam or 8 MP Raspberry Pi Camera or Video(.h264 format)

Option:
- 7" 1024x600 capacitive touch monitor
- Android Phone 

Test on:

- Jetson Xavier, nano, JetPack 4.4/4.5.1, Video, USB webcam, and Android Phone. 

## Installation

### Requirements:

- [NVIDIA DeepStream](https://developer.nvidia.com/deepstream-sdk) 5.0
- MQTT Client
- Mosquitto MQTT Broker
- Download sample data
- Download trained model data

Option: 
- Azure IoT Device
- Open Distro for ElasticSearch 
- Open Distro for Kibana 
- Azure Virtual Machine

#### 1. Clone this repository 
```
$ git clone <this repo>
```
#### 2. To install DeepStream SDK
Installing the five methods. Using the DeepStream tar package here.  
Download package [here](https://developer.nvidia.com/deepstream-getting-started) .

```
$ sudo tar -xvf deepstream_sdk_<deepstream_version>_jetson.tbz2 -C /
$ cd /opt/nvidia/deepstream/deepstream-5.0
$ sudo ./install.sh
$ sudo ldconfig
```
See [NVIDIA DeepStream SDK Developer Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Quickstart.html#install-the-deepstream-sdk) , and more.  

Python Bindings
```
$ cd /opt/nvidia/deepstream/deepstream-5.0/lib
$ sudo python3 setup.py install
```

See [NVIDIA DeepStream SDK Developer Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Python_Sample_Apps.html#metadata-access) , and more.


#### 3. Download sample data
Please download the sample data [here](https://drive.google.com/drive/folders/1YnxqMk-S5a3rMu-o41HBxX60h9rVc5m8?usp=sharing). (Google Drive link)

#### 4. Download models 
 Download the models dir from [here](https://drive.google.com/drive/folders/1LBr1fiOOBtGEzRAF3RXIBdOfjg-kgFRT?usp=sharing). (Google Drive link)

Tree after download models dir:
```
<this repo>
	|- common
	|- config
	|- data
	|- kibana
	|- models
		|- peoplenet (in 4 files)
	|- mobile
	|- scripts
	|- src
```

### Option1: Send a message alert to mobile phone
#### 1. (Option1) To install MQTT Client
```
$ pip3 install paho-mqtt
```

#### 2. (Option1) To install Mosquitto MQTT Broker
```
$ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
$ sudo apt update
$ sudo apt install mosquitto
```

#### 3. (Option1) To install Mobile App  

Please access the APK link below in your Android phone and allow to install.

[PFAClientApp-Alpha2.apk](https://drive.google.com/drive/folders/1qEHUzzTnI7vqAFdPu-gjk2ka0yYUPykv?usp=sharing)


#### 4. (Option1) Mobile Connection Setup
1. On Linux terminal, start the mosquitto message broker service
	```	
	$ sudo service mosquitto start
	```

2. Using "PFA Client" mobile application, select to connection button. 
	Once connection is established, the application is now readdy to receive the message alerts.  

3. Edit the MQTT Host in `config/pfa_config.ini` (which should be line 34)
	```
	#Your Jetson IP address 
	HOST ="<Jetson IP address>"
	```

Note: 
1. Stopping the mosquitto message broker service will disable mobile connections to all PFA client applications

	```
	$ sudo service mosquitto stop
	```

2. Mobile and Jetson must be connected in the same area network.

### Option2: send a message alert to Azure IoT and Open Distro for Elasticsearch and Kibana
#### 1. (Option2) To install Azure IoT Device 
```
$ pip3 install azure-iot-device
```

#### 2. (Option2) To install Open Distro for Elasticsearch and Kibana
Please refer to the [README guide](kibana/README.md) in Kibana dir for the setup details.  
 
## Usage

#### 0. (Option1) Start mosquitto message broker service to enable alert notification to Mobile application

```
$ sudo service mosquitto start
```

### 1. Run the command
#### Using Video(.h264 format) or sample data

```
$ cd script
$ python3 main.py [VIDEO/FILE/PATH]

#Use sample data
$ python3 main.py ../data/2020-08-27_15-12-31.264
```  
#### Using USB webcom or Raspberry Pi Camera
1. Edit the Camera flag in `config/pfa_config.ini` (witch should be line 97):
```
#USB webcom (default)
COM_MODE = 0

#Raspberry Pi Camera
COM_MODE = 1
```

2. Run the command
```
$ cd script
$ python3 main.py
```

### 2. Camera view calibration 
After run the command, wait for stream to show.

1. While streaming, double click 4 corners(top-left, top-right, bottom-left, bottom-right)

2. Then, stream with 2D map view will appear

3. People detection and tracking will be automatically displayed after the calibration process
 
Note: Edit the `config/pfa_config.ini` of initial configuration setting as you wish. The settings for the following are included in the file:

- IOT Hub Client Setting
- Mobile Client Setting
- Aspect Ratio
- Pixel dimension per feet (Grid Size)
- Dwell Time limitation (in second) for alert
- Dwell Time Average limitation for alert

#### 3. (Option2) Connect to the internet to enable alert notification to Azure IoT hub -> Open Dstro for Kibana.


##  Data analysis and visualization

Data analysis and visualization with Open Distro for Kibana.  
After access and login the Open Distro for Kibana, create Visualization and Dashboard.
Refer to the [README guide](kibana/README.md#Create-visualization-and-Dashboard) in kibana directory for the creating visualization details.




## Licenses
Copyright (C) 2020, Ryoyo-NV All rights reserved.  
The models and sample data are available for research, development, and PoC purposes only.

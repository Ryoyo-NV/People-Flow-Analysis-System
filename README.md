# People Flow Analysis System

A low-cost People Flow Analysis System developed using NVIDIA's Jetson and Deepstream SDK, integrated with high quality open source software and library.

The system is able to monitor every person within the camera vision. Each person detected will be tracked giving a unique track ID and a green bounding box will be drawn on it. When the detected person stay on the same spot for a certain duration, the system will send a message alert to an authorized Azure Iot Hub and android mobile phone. The message alert constains time, track id and location. 

There is also a calibration process to define the ground surface mapping from the camera view. The calibration input will be set by the user.

<img src="src/people_flow_analysis_demo.gif" hight="480"/>


## Prerequisite

- NVIDIA Jetson Platform
- [JetPack](https://developer.nvidia.com/embedded/jetpack) 4.4
- USB webcam or 8 MP Pi Camera or Video(.h264 format)

Option:
- 7" 1024x600 capacitive touch monitor

Test on:

- Jetson Xavier nano, JetPack 4.4, Video, and USB webcam. 

## Installation

### Requirements:

- [NVIDIA DeepStream](https://developer.nvidia.com/deepstream-sdk) 5.0
- SORT dependencies (filterpy,scikit-image,lap)
- MQTT Client
- Mosquitto MQTT Broker
- Download sample data
- Download trained model data
- Azure IoT Device
- Open Distro for ElasticSearch 
- Open Distro for Kibana 
- Azure Visual Machine


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


#### 3. To install SORT 

```
$ sudo apt install liblapack-dev libblas-dev gfortran 
$ sudo pip3 install filterpy==1.4.5
$ pip3 install scikit-image==0.17.2
$ pip3 install lap==0.4.0
```

#### 4. Download sample data
Please download the sample data in [Gdrive data link](https://drive.google.com/drive/folders/1FuzkG_qyEnLudL6LgIP9xKrCClFKcsKW)

#### 5. To install MQTT Client
```
$ pip3 install paho-mqtt
```

#### 6. To install Mosquitto MQTT Broker
```
$ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
$ sudo apt update
$ sudo apt install mosquitto
```

#### 7. To install Mobile App  

Please access the APK link below in your Android phone and allow to install.

[PFAClientApp-Alpha2.apk](https://drive.google.com/drive/folders/1zAMG0OcnXf-EKDMMqg99PL0fIylpTnp-)

Usage of the mobile application is presented in the [demo video](src/people_flow_analysis_demo.gif). 

#### 8. Mobile Connection Setup
1. On Linux terminal, start the mosquitto message broker service
	```	
	$ sudo service mosquitto start
	```

2. Using "PFA Client" mobile application, select to connection button. 
	Once connection is established, the application is now readdy to receive the message alerts.  

Note: 
1. Stopping the mosquitto message broker service will disable mobile connections to all PFA client applications

```
$ sudo service mosquitto stop
```
2. Mobile and Jetson must be connected in the same area network.

#### 9. To install Azure IoT Device 
```
$ pip3 install azure-iot-device
```

#### 10. To install Open Distro for Elasticsearch and Kibana
Please refer to the [README guide](kibana/README.md) in Kibana dir for the setup details.

 
## Usage

## Running the Application

People Flow Analysis System is configured to work with DeepStream SDK 5.0 with Python Bindings installation. 



3. Download the models folder from the [GDrive link](https://drive.google.com/drive/folders/1ZGrdZd7QUYO3_X3DO7HcEQt4n8VYJ6S-).

4. Navigate to the application directory and copy the downloaded data folder here.

     `$ cd pfasys/`
   
5. Run the program.

	`$ cd pfasys/script`

     `$ python3 main.py <video file path>`

     	e.g. $ python3 main.py /home/username/pfasys/data/pedestrian2_720p.264

    NOTE: This system version is tested using video stream file input. 


## Using the Application

**Initial configuration settings**
1. Edit the 'pfa_config.ini' file located in the path below. 

	`$ gedit pfasys/config/pfa_config.ini`

	Instruction on the needed intial configuration settings for the following are included in the file.

		- IOT Hub Client Setting
		- Mobile Client Setting
		- Aspect Ratio
		- Pixel dimension per feet (Grid Size)
		- Dwell Time limitation (in second) for alert
		- Dwell Time Average limitation for alert


2. (OPTIONAL) Start mosquitto message broker service to enable alert notification to Mobile application

	`$ sudo service mosquitto start

3. (OPTIONAL) Connect to the internet to enable alert notification to Azure IoThub -> Kibana.


**A. Camera View Calibration**
1. Run 'python3 main.py'
2. Wait for stream to show
3. While streaming, double click 4 corners(top-left, top-right, bottom-left, bottom-right)
4. Then, stream with 2D map view will appear
5. People detection and tracking will be automatically displayed after the calibration process

    NOTE: To redo the calibration, please delete the 'pfasys/config/calibration_config.txt' file.


**B. People detection and tracking**

	Video stream automatically displayed when the program starts once calibration is already done.


**C. Quit/Terminate program**

    Press "q" in video stream window.


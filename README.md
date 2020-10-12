# People Flow Analysis System

A low-cost People Flow Analysis system developed using NVIDIA's Jetson Nano and Deepstream SDK, integrated with high quality open source software and library.

The system is able to monitor every person within the camera vision. Each person detected will be tracked giving a unique track ID and a green bounding box will be drawn on it. When the detected person stay on the same spot for a certain duration, the system will send a message alert to an authorized Azure Iot Hub and android mobile phone. The message alert constains time, track id and location. 

There is also a calibration process to define the ground surface mapping from the camera view. The calibration input will be set by the user.


<img src="video/SCOPE2-oss_release_candidate.mp4.gif" hight="480"/>

**Hardware Setup:**

	NVIDIA Jetson Nano with at least 32gb SD card
	7" 1024x600 capacitive touch monitor
	8 MP Pi Camera 

**Setup pre-requisites:**

	JetPack SDK 4.4 Developer Preview
	NVIDIA DeepStream SDK 5.0 Developer Preview
	DeepStream SDK Python Bindings
	Python 3.6
	Gst-python
	SORT dependencies (filterpy,scikit-image,lap)
	MQTT Client
	Azure IoT Device SDK
	Mosquitto MQTT Broker
	Download sample data
	Download trained model data


## Installing Pre-requisites in Jetson Nano:

**Jetpack SDK 4.4 Developer Preview:**

 Download and install from [NVIDIA Jetpack SDK](https://developer.nvidia.com/jetpack-sdk-44-dp-archive) archive

**DeepStream SDK 5.0 Developer Preview:**

 Download and install from [NVIDIA Deepstream SDK](https://developer.nvidia.com/embedded/deepstream-on-jetson-downloads-archived) archive

**DeepStream SDK Python Bindings**

Download the [Python Bindings](https://drive.google.com/drive/folders/18bnRlgsENRl8Enl6DCqd4YcYZvNPO2AW) 
release package from the link and unpack it under Deepstream 5.0 installation

	$ tar xf ds_pybind_v0.9.tbz2 -C <DeepStream 5.0 ROOT>/sources

**Gst-python:**

Should be already installed on Jetson.
If missing, install with the following steps:

	$ sudo apt update
	$ sudo apt install python3-gi python3-dev python3-gst-1.0 -y

**SORT dependencies:**

	$ sudo apt install liblapack-dev libblas-dev gfortran 
	$ sudo pip3 install filterpy==1.4.5
	$ pip3 install scikit-image==0.17.2
	$ pip3 install lap==0.4.0


**Download sample data**

Please download the sample data in [Gdrive data link](https://drive.google.com/drive/folders/1FuzkG_qyEnLudL6LgIP9xKrCClFKcsKW)

**MQTT Client:**

	$ pip install paho-mqtt

**Azure IoT Device SDK:**

	$ pip install azure-iot-device

**Mosquitto MQTT Broker:**

	$ sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
	$ sudo apt-get update
	$ sudo apt-get install mosquitto

**Install Mobile App:**

Please access the APK link below in your Android phone and allow to install.

[PFAClientApp-Alpha2.apk](https://drive.google.com/drive/folders/1zAMG0OcnXf-EKDMMqg99PL0fIylpTnp-)

Usage of the mobile application is presented in the demo video file. 

**Mobile Connection Setup:**

	1. On Linux terminal, start the mosquitto message broker service
		sudo service mosquitto start

	2. Using "PFA Client" mobile application, select to connection button. 
	   Once connection is established, the application is now readdy to receive the message alerts.  

	Note: 1. Stopping the mosquitto message broker service will disable mobile connections to all PFA client applications
	       		sudo service mosquitto stop
	      2. Mobile and Jetson Nano must be connected in the same area network.

**Kibana:**

Please refer to the README guide in Kibana folder for the setup details.

Usage of the Kibana Dashboard is presented in the demo video file. 


## Running the Application

People Flow Analysis System is configured to work with DeepStream SDK 5.0 with Python Bindings installation. 

1. Extract the pfasys_candidate_rel.zip

2. Confirm the Deepstream and Python Bindings PATH declaration inside /pfasys/common/is_aarch_64.py

	`$ gedit /pfasys/common/is_aarch_64.py`
	
	DS_PATH='/opt/nvidia/deepstream/deepstream-5.0'
	
	PY_PATH=DS_PATH+'/sources/python/bindings/'

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


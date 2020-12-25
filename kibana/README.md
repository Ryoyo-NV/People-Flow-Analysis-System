# Open Distro for Elasticsearch
This is for visualizing information gathered by the Azure IoT Hub from the
Jetson devices. The following documents the installation and setup
of the Open Distro for Elasticsearch(Elasticsearch, Kibana) on the Azure VM.

## Prerequisite

- Azure IoT Hub
### Azure IoT Hub resource and IoT Device setup

####  Create IoT Hub
   1. Go to [Azure Portal](https://portal.azure.com/), type on the search bar "IoT Hub" or click on "IoT Hub".

   2. Click the +Add button to add the new IoT hub resource.

   3. Fill in the information in the Basics tab.

   4. On the "Size and scale" tab, select the desired tier in the `Pricing and scale tier`.

      **Note:** F1 tier is the free tier for IoT Hub that only accepts up to 8000 messages/day
   5. Click on the "Review + create" tab and wait until it is accepted, then click the "Create" button.

   6. Wait until the deployment is complete, and your newly created IoT Hub resource will be displayed.
   
   See [Create an IoT hub using the Azure portal](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-create-through-portal#create-an-iot-hub), and more.
#### Register your Jetson device 

   1. To add your Jetson device in IoT hub resource, select the IoT hub resource and click IoT devices from left pane menu.
   
   2. Click the "+New" button and enter the desired device ID, then click "Save" button.
   
   3. Select the newly added IoT device, copy the Primary connection String value. 
      This will serve as the connection string for the IoT device to send messages to Azure IoT hub.
   
   See [Register a new device in the IoT hub](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-create-through-portal#register-a-new-device-in-the-iot-hub), and more.

   4. Edit `config/pfa_config.ini`, paste the coped Primary connection String value as follow:
     
   ```
   #HOST_NAME = <iot hub hostname>
   #DEVICE_ID = <iot device id>
   #SHARED_ACCESS_KEY = <iot device shared access key>
   ```

## Installation

### Requirement:

- Azure Virtual Machine 

  - Dcoker  
  - docker-compose
  - [Open Distro for Elasticsearch](https://opendistro.github.io/for-elasticsearch/)
  - Open Distro for Kibana
  - logstash 

Note: 
- Creating Virtual Machines in Azure is **not free**.
- Open Distro for Elasticsearch can on-premise using [Docker image](https://opendistro.github.io/for-elasticsearch-docs/docs/install/docker/).

### Virtual Machine on Azure
**Note:** Creating virtual machines in Azure is not free. 

   1. From the Azure Portal, go to the **Marketplace**.
   2. Search for **Virtual Machine**. Then click the **Add** button.
   3. Fill-in the required information for the following tabs: 

		**Basics**
		
			a. Select available subscription
			b. Create a new resource group and enter your desired resource group
			c. Enter virtual machine name
			d. Set the region for deployment (Japan West etc.)
			e. Set Availability options to “No infrastructure redundancy required”
			f. Set image to Ubuntu Server 18.04 LTS Gen 1
			g. Set size your desired RAM size
				 Note: We recommend allowing Docker to use at least 4 GB of RAM
			h. Set authentication type to “Password”
			i. Enter username and password
			j. Set inbound ports to SSH (22)

		**Disks**
		
		 	a. Set OS disk type to Standard SSD
			b. Set Encryption type to Default

		**Networking**
		
		 	a.Set NIC network security group to Basic
			b.Set Public inbound ports to Allow selected ports
			c.Set Accelerated networking to Off

	 	**Management**
		
			a. Disable Boot Diagnostics
			b. Set OS guest diagnostics to Off
			c. Set System assigned managed identity to Off
			d. Set Enable backup to Off

   4. Click Review and Create to see the summary

   5. Click Create to create VM
   
   6. Go to the newly create VM
#### Add inbound port rule   

   1. Go to networking
   
   2. Click Add inbound port rule
   
   3. Change Destination port ranges to 5601
   
   4. Change Priority to 110
   
   5. Enter desired Name
   
   6. Click Add

### Docker and docker-compose installation and setup

1. ssh to the VM

```
$ ssh <username>@<ip address of vm>
```
2. Enter password of VM

#### 3. To install  Docker

```
$ sudo apt update
$ sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
$ sudo apt update
$ sudo apt install docker-ce
$ sudo systemctl status docker
```

#### 4. To install docker-compose

```
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ sudo docker-compose --version
```

Check docker version to know if docker is running

```
$ sudo docker --version
```

#### 5. Pull docker image

```
#Open-Distro for Elasticsearch and Kibana
$ sudo docker pull amazon/opendistro-for-elasticsearch:1.10.1
$ sudo docker pull amazon/opendistro-for-elasticsearch-kibana:1.10.1

#logstash oss
$ sudo docker pull docker.elastic.co/logstash/logstash-oss:7.9.1
$ sudo docker images
```

#### 6. Create custom docker-compose.yml 
Create custom docker-compose.yml file inside open-distro folder

```
$ cd /home
$ sudo mkdir open-distro
$ cd open-distro
$ sudo touch docker-compose.yml
$ sudo vim docker-compose.yml
```
   *See [docker-compose.yml](config/docker-compose.yml) as reference*
   
#### 7. Create custom logstah.conf
Create custom logstash.conf inside open-distro folder.
```
$ cd /home/open-distro
$ sudo touch logstash.conf
$ sudo vim logstash.conf
```

**Change event_hub_connections**

1. Retrieve the connection string endpoint by accessing the **Azure IoT Hub > Built-in endpoints.**

2. Under the **Event Hub compatible endpoint** section, set the shared access policy to **service**.

3. Copy the value shown in** Event Hub-compatible endpoint.**

4. Paste the copied connection string endpoint to the **event_hub_connections** in **logstash.conf** file.

   *See [logstash.conf](config/logstash.conf) as reference*  
   See [Read from the built-in endpoint](https://docs.microsoft.com/ja-jp/azure/iot-hub/iot-hub-devguide-messages-read-builtin#read-from-the-built-in-endpoint), and more.

## Run Open Distro for Elasticsearch
```
$ sudo add-apt-repository ppa:openjdk-r/ppa
$ sudo apt update
$ sudo apt install openjdk-11-jdk
$ sudo apt install unzip
$ wget -qO - https://d3g5vo6xdbdb9a.cloudfront.net/GPG-KEY-opendistroforelasticsearch | sudo apt-key add -
$ echo "deb https://d3g5vo6xdbdb9a.cloudfront.net/apt stable main" | sudo tee -a   /etc/apt/sources.list.d/opendistroforelasticsearch.list
$ sudo wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-oss-7.9.1-amd64.deb
$ sudo dpkg -i elasticsearch-oss-7.9.1-amd64.deb
$ sudo apt-get update
$ sudo apt install opendistroforelasticsearch
$ sudo apt install opendistroforelasticsearch-kibana
```

1. Edit custom kibana.yml 
Go to directory etc/kibana/
Use elasticsearch.hosts: ELASTICSEARCH_HOSTS  instead of elasticsearch.url  
   *See [kibana.yml](config/kibana.yml) as reference*

2. Run, Elasticsearch, Kibana and Logstash containers
```
$ cd /home/open-distro
$ sudo docker-compose up
```

Note: If error is encountered in one of the containers, run this command
```
$ sudo docker-compose down -v
```
then
```
$ sudo docker-compose up
```
      
## Operation Instructions
### Starting containers
1. Start the Elasticsearch, Kibana, and Logstash containers.
```
$ sudo docker-compose start
```
2. Make sure the Elasticsearch, Kibana, and Logstash containers are up and running.
``` 
$ sudo docker ps
```
Note: Status column should have the value "Up"

3. To install azure event hub plugin, access the logstash
```
$ sudo docker exec -it logstash bash
```
4. Install the azure event hub plugin using the command
```
$ /usr/share/logstash/bin/logstash-plugin install logstash-input-azure_event_hubs
```
Note: if you don't know where is your logstash, you can find the location using:
```
$ whereis logstash
```
5. Start Elasticsearch service
```
$ sudo systemctl start elasticsearch.service
```
6. Start Kibana service
```
$ sudo systemctl start kibana.service
```
7. Check the status of the services using the below command respectively:
```
$ sudo systemctl status elasticsearch.service
$ sudo systemctl status kibana.service
```

8. Access the Kibana 
After starting Kibana, you can access it at port 5601.
```
http://<ip address of VM>:5601 
```
9. login the Kibana
```
username: admin
password: admin
```

---

## Create visualization and Dashboard

### 1. Creating Indexes
   1. On the menu, click **Stack Management** under Management.
   2. Click **Index Patterns.**
   3. Click **Create Index Pattern.**
   4. Input the desired string pattern to select from the list of indices. Then click the **Next step** button.
   5. Select the **message.time** field for time filtering. Then click the **Create index pattern** button. 
   6. The next page shows the list of fields of the selected indexes.
   
   
### 2. Creating Visualizations
**Dweller Count**
1. On the menu, click **Visualize.**
2. Click the **Create visualization** button.
3. From the list of visualizations, click **Vertical Bar** visualization.
4. Select the index to use.
5. Expand the **Y-axis** under **Metrics.**
6. Select **Count** as Aggregation and set the label name to **Customers.**
7. Click the **Add** button under **Buckets** and select **X-axis.**
8. Select **Date Histogram** as Aggregation. Set **message.time** for the Field. Set **Day** for the Minimum interval. Set the label name to **Period.**
9. Click the **Update** button.
10. Click the **Save** button.
11 .Set the Title for the visualization to **Dweller Count**. Optionally, you can enter the description for the visualization. Then click the **Save** button.

**Dweller Peak Times**
1. On the menu, click **Visualize.**
2. Click the **Create visualization** button.
3. From the list of visualizations, click **Vertical Bar** visualization.
4. Select the index to use.
5. Expand the **Y-axis** under **Metrics.**
6. Select **Count** as Aggregation and set the label name to **Customers.**
7. Click the **Add **button under **Buckets** and select **X-axis.**
8. Select **Date Histogram** as Aggregation. Set **message.time** for the Field. Set **Hour** for the Minimum interval. Set the label name to **Time.**
9. Click the **Update** button.
10. Click the **Save** button.
11. Set the Title for the visualization to **Dweller Peak Times**. Optionally, you can enter the description for the visualization. Then click the **Save** button.

**Dweller Count Year Overview**
1. On the menu, click **Visualize.**
2. Click the **Create visualization** button.
3. From the list of visualizations, click **Pie** visualization.
4. Select the index to use.
5. Expand the **Slice size** under **Metrics.**
6. Select **Count** as Aggregation and set the label name to **Customers.**
7. Click the **Add** button under Buckets and select Split slices.
8. Select **Date Histogram** as Aggregation. Set **message.time** for the Field. Set **Month** for the Minimum interval. Set the label name to Month.
9. Click the **Update** button.
10. Click the **Save** button.
11. Set the Title for the visualization to **Dweller Count Year Overview**. Optionally, you can enter the description for the visualization. Then click the **Save** button.

### 3. Creating Dashboard
1. On the menu, click **Dashboard.**
2. Click the **Create Dashboard** button.
3. Click **Add** link.
4. On the **Add Panels** panel, click the **Dweller Count**, **Dweller Peak Times**, and **Dweller Count Year Overview** visualizations. Then click the close button.
5. Set the Time Filter to display data for the current day.
6. On the **Dweller Count visualization**, click the **gear** icon on the top-right of the visualization.
7. Click **Edit visualization.**
8. Click **Add filter**
9. Set field to **@timestamp** and operator to **is between**
10. Set the time range to the current month.
11. On the **Dweller Count Year Overview** visualization, click the **gear** icon on the top-right of the visualization.
12. Click **Edit visualization.**
13. Click Add filter
14. Set field to **@timestamp** and operator to **is between**
15. Set the time range to the current year.
16. Click **Save** link.
17. Set the Title to PFA Dashboard.
18. Click on the **Store time with dashboard.**
19. Click the **Save** button. 

### 4. Advanced Settings
1.On the menu, click Stack Management.
2.Click Advanced Settings.
3.Look for Scaled date format.
4.Add the following blue highlighted text into the textbox. Modify into the specified green highlighted text in the textbox as shown below,
```
[
  ["", "HH:mm:ss.SSS"],
  ["PT1S", "HH:mm:ss"],
  ["PT1M", "HH:mm"],
  ["PT1H", "HH:mm"],
  ["P1DT", "MMM-DD"],
  ["P1MT", "MMMM"],
  ["P1YT", "YYYY"]
]
```
5.A notification at the bottom pops up. Click Save Changes button. 

### Stopping containers
1. Access Kibana VM
2. Stopping the Kibana service,
```
$ sudo systemctl stop kibana.service   
```
3.Stopping Elasticsearch service,
```
$ sudo systemctl stop elasticsearch.service
```
4. Stopping all containers
```
$ sudo docker-compose stop
```

## Known Issues
1. ERROR: for odfe-node1. Cannot start service odfe-node1: listen tcp 0.0.0.0:9600: bind: address already in use. (Errors occurs when you run/up the docker-compose but the elasticsearch.service was already running.)

      a.Check status of Elasticsearch service if running:
      ```
      $ sudo systemctl status elasticsearch.service
      ```
      b.If running, stop the service.
      ```
      $ sudo systemctl stop elasticsearch service
      ```
      c.Stop docker-compose
      ```
      $ sudo docker-compose down –v
      ```
      d.Start again the docker-compose.
      ```
      $ sudo docker-compose up
      ```

# People Flow Analysis System
# Elastic Stack
This is for visualizing information gathered by the Azure IoT Hub from the
Jetson Nano devices. The following documents the installation and setup
of the Elastic Stack (Logstash, Elasticsearch, Kibana) on the Azure Cloud environment.

## Prerequisite
### Azure IoT Hub resource and IoT device setup
   1. Go to Azure Portal, type on the search bar "IoT Hub" or click on "IoT Hub".
   2. Click the +Add button to add the new IoT hub resource.
   3. Fill in the information in the Basics tab.
   4. On the "Size and scale" tab, select the desired tier in the `Pricing and scale tier`.

      **Note:** F1 tier is the free tier for IoT Hub that only accepts up to 8000 messages/day
   5. Click on the "Review + create" tab and wait until it is accepted, then click the "Create" button.
   6. Wait until the deployment is complete, and your newly created IoT Hub resource will be displayed.
   7. To add your Jetson device in IoT hub resource, select the IoT hub resource and click IoT devices from left pane menu.
   8. Click the "+New" button and enter the desired device ID, then click "Save" button.
   9. Select the newly added IoT device, copy the Primary connection String value. 
      This will serve as the connection string for the IoT device to send messages to Azure IoT hub.

   **References:**
   * Create IoT Hub: https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-create-through-portal
   * Connect IoT device to Azure IoT Hub: https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-raspberry-pi-kit-node-get-started

### logstash.conf file Preparation

   **Retrieve the connection string endpoint**
   1. Select the added IoT device menu in IoT hub resource and go to "Built-in endpoints"
   2. Under the Event Hub compatible endpoint section, set the Shared access policy to service.
   3. Copy the value shown in Event Hub-compatible endpoint.
   4. Download the logstash.conf file found in the logstash folder.
   4. Paste the copied connection string endpoint to the event_hub_connections in logstash.conf file.

## Installation
### Elastic Stack on Azure
**Note:** Creating virtual machines in Azure is not free. Alternatively, Elastic Stack can be created on-premise.

   1. From the Azure Portal, go to the **Marketplace**.
   2. Search for **Elasticsearch (Self-Managed)**. Then click the **Create** button.
   3. Fill-in the required information for the following tabs,

   **Basics**
      
      a. Select available Subscription
      b. Create a new Resource group
      c. Set the Region for deployment
      d. Enter desired Username
      e. Enter desired Password and Confirm password

   **Cluster Settings**

      a. Confirm that the latest Elasticsearch version is selected (v7.8.0 as of documentation)
      b. Enter desired Cluster name

   **Nodes Configuration**

      a. (Optional) Set Hostname prefix
      b. Set Number of data nodes to 1
      c. Select Yes for Data nodes are master eligible

   **Kibana & Logstash**

      a. Set Yes for Install Kibana?
      b. Set Yes for Install Logstash?
      c. Set number of Logstash VMs to 1
      d. On Logstash config file, upload the prepared "logstash.conf" file
      e. Enter azure_event_hubs on Additional Logstash plugins

   **Security**

      a. Enter desired passwords for each default user accounts

   **Certificates**

      a. SSL Certificates are not involved in this setup. Set No for Configure Transport Layer Security

   *Note: Azure only allows a Total Regional Cores quota of 4. Requiring more cores would require to submit a request for Quota increase with Microsoft Support.

   4. Click the **Review + create** button and wait until deployment is complete, then select **Create** button.

## Running Elastic Stack
Accessing Elastic Stack is done via PuTTY or other similar tools.

**Note:** By default, Kibana and Elasticsearch are run as a service after the VMs are created.

1. Retrieve the Kibana **DNS name** in the **Overview** panel of the Kibana VM in Azure. This will be used to access via PuTTY.

2.	Access the Kibana VM perform the following,
* Access via PuTTY or similar tools

**Host Name** – the DNS name of Kibana retrieved from step 1.

**Username** – the username created from **Elastic Stack on Azure, Step 3, Basics** section, **d**.

**Password** – the password created from **Elastic Stack on Azure, Step 3, Basics** section, **e**.
* Access via Linux terminal. Please note, `<kibana DNS name>` refers to the **DNS name** retrieved from Step 1.
```
$ ssh <username>@<kibana DNS name>
```
3.	Confirm that Kibana is running.
```
$ service kibana status
```
if the status is not running, start the Kibana service
```
$ sudo service kibana start
```
4.	Access Elasticsearch VM and confirm that Elasticsearch is running.
Please note, if you set the Hostname prefix from **Installation, Elastic Stack on Azure, Step 3, Nodes Configuration, a.**, prepend data-0 with the set prefix. For instance, if the prefix was `pfa`, the VM will be `pfadata-0`
```
$ ssh <username>@data-0
$ service elasticsearch status
```
if the status is not running, start the Elasticsearch service
```
$ sudo service elasticsearch start
```
5.	Access Logstash VM.
Please note, if you set the Hostname prefix from **Installation, Elastic Stack on Azure, Step 3, Nodes Configuration, a.**, prepend logstash-0 with the set prefix. For instance, if the prefix was `pfa`, the VM will be `pfalogstash-0`
```
$ ssh <username>@logstash-0
```
6.	Add the password of elastic user to the keystore file
```
$ sudo /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add ELASTIC_PASSWORD
```
7.	Execute Logstash
* To run Logstash as a service,
```
$ sudo service logstash start
```
* To run Logstash manually,
```
$ sudo /usr/share/logstash/bin/logstash --path.settings /etc/logstash
```
8. You can now access Kibana via browser using the DNS Name of kibana with port 5601.

**Note:**
* `<username>` is retrieved from the IV. Installation, **A. Elastic Stack on Azure, Step 3, Basics** section, **d**.
* In the event an error is encountered when executing the command above, please refer to **Known Issues, A. Corrupted keystore file on Logstash host** section.
* When entering the value for **ELASTIC_PASSWORD**, enter the password inputted on Elastic user account from **Installation, A. Elastic Stack on Azure, Step 3, Security** section.


## Known Issues
1. **Corrupted keystore file on Logstash host**. This is encountered when trying to execute Logstash
   and displays an error that it cannot read */etc/logstash/logstash.keystore* file or cannot read
   *${ELASTICSEARCH_URL}* and *${LOGSTASH_SYSTEM_PASSWORD}* variables. This is identified with the
   following message when interacting with logstash-keystore,

   ```
   Found a file at /etc/logstash/logstash.keystore, but it is not a valid Logstash keystore.
   ```

a. Remove the keystore file.
  ```
  $ sudo rm -rf /etc/logstash/logstash.keystore
  ```
b. Create a new keystore file.
  ```
  $ sudo /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash create
  ```
c. Add the necessary keys. Then input the value when asked.
```
$ sudo /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add ELASTICSEARCH_URL
$ sudo /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add LOGSTASH_SYSTEM_PASSWORD
$ sudo /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add ELASTIC_PASSWORD
```
Note: 
*	When entering the value for **ELASTICSEARCH_URL**, enter the computer name of the Elasticsearch virtual machine. For instance, if the computer name is data-0, the ELASTICSEARCH_URL value should be **http://data-0:9200**.
*	When entering the value for **LOGSTASH_SYSTEM_PASSWORD**, enter the password inputted on **Logstash system user account** from **IV. Installation, A. Elastic Stack on Azure, Step 3, Security section**.
*	When entering the value for **ELASTIC_PASSWORD**, enter the password inputted on **Elastic user account** from **IV. Installation, A. Elastic Stack on Azure, Step 3, Security section**.

2. **Alert Message not received after machine restart**. When shutting down the virtual machines are performed regularly, various errors will occur where logstash couldn’t read logstash.keystore file due to permission issues. As of documentation, an appropriate fix doesn’t exist. But the following workaround can mitigate this issue. •	After starting the Logstash VM from shutdown state and starting the logstash service, logstash doesn’t receive data from Azure IoT Hub.

a.	Delete the logstash configuration from the sysconfig directory
```
$ sudo rm -rf /etc/sysconfig/logstash
```
b.	Change the user and group to `root` in the logstash.service file
```
$ sudo nano /etc/systemd/system/logstash.service
```

logstash.service
```
[Service]
Type=simple
User=root
Group=root
```
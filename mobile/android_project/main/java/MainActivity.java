package com.example.mqttclient;

import androidx.activity.OnBackPressedCallback;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationCompat;

import android.app.AlertDialog;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Point;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Vibrator;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

//class MainActivity
//Description: MainActivity of mobile application
//      Connect/Disconnect to server
//      Subscribe to topic
//      Display received messages
//Parameter: None
//Return: None
@RequiresApi(api = Build.VERSION_CODES.O)
public class MainActivity extends AppCompatActivity {


    //initialize list view
    ListView listView;
    //initialize text view
    TextView connectionStatus;
    //initialize switch button
    Switch switchButton;
    //initialize edit text
    EditText editText;
    //initialize bmp
    Bitmap bmp;
    //initialize mesPayload: holds the message received
    String mesPayload;
    //initialize topic data
    String topicData = "topic/data";
    //initialize topic image
    String topicImage ="topic/image";
    //initialize mqttHost: holds the mqtt host
    String mqttHost;
    //generate client id
    String clientId = MqttClient.generateClientId();
    //initialize message list
    ArrayList<String> message_list = new ArrayList<String>();
    //initialize adapter
    ArrayAdapter<String> adapter;
    //initialize mqtt android client
    MqttAndroidClient client;
    //initialize notification manager
    NotificationManager notificationManager;
    //initialize vibrator
    Vibrator vibrator;
    //initialize byteContent
    byte[] byteContent;
    String getTime;


    //function onCreate
    //Description: initializes MainActivity that connects to mqtt broker
    //Parameter: activity_main
    //Return Value: None
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //call backButtonEvent function
        backButtonEvent();
        //call readFile function
        readFile();
        //edit button linked to our xml
        editText = (EditText) findViewById(R.id.editHost);
        //switch button linked to our xml
        switchButton = (Switch) findViewById(R.id.switch1);
        //textView object linked to our xml
        connectionStatus = (TextView) findViewById(R.id.textView);
        //editText object linked to our xml
        editText.addTextChangedListener(loginTextWatcher);
        //listView object linked to our xml
        listView = (ListView) findViewById(R.id.listView1);
        vibrator = (Vibrator) getSystemService(VIBRATOR_SERVICE);

        //set message_list to be displayed in listview
        adapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, message_list);
        listView.setAdapter(adapter);


        //get system service of notification
        notificationManager = (NotificationManager) MainActivity.this.getSystemService(Context.NOTIFICATION_SERVICE);

        //ui to connect and disconnect to server using switch button
        switchButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //connect to mqtt broker if switch button is on
                if (switchButton.isChecked()) {
                    //disable edit text
                    editText.setEnabled(false);
                    //set connectionStatus text to "waiting to connect"
                    connectionStatus.setText("waiting to connect...");
                    //add tcp and port 1883
                    mqttHost = "tcp://"+ editText.getText().toString() + ":1883";
                    //set client
                    client = new MqttAndroidClient(MainActivity.this, mqttHost, clientId);
                    System.out.println("HOST: " + mqttHost);
                    //call Connect function
                    Connect();
                }
                //disconnect to mqtt broker if switch button is off
                else {
                    //enable edit text
                    editText.setEnabled(true);
                    //call Disconnect function
                    Disconnect();
                }
            }
        });


        //on item click on listview, proceed to location view
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                //initialize intent to Activity_ImageView class
                Intent intent = new Intent(view.getContext(), Activity_ImageView.class);
                //get the value of item clicked to be passed on Activity_ImageView
                String val =(String) adapterView.getItemAtPosition(i);
                System.out.println("GET ITEM POS: "+ adapterView.getItemAtPosition(i));
                //create a key to be identified in Activity_ImageView
                intent.putExtra("key",val);
                //start intent
                startActivity(intent);
                //remove notification if item is clicked
                notificationManager.cancelAll();
            }
        });


        //function to delete item if long pressed
        listView.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
            @Override
            public boolean onItemLongClick(AdapterView<?> arg0, View arg1,
                                           final int pos, long id) {
                //build dialog box
                AlertDialog.Builder builder1 = new AlertDialog.Builder(MainActivity.this);
                //set dialog box message
                builder1.setMessage("Are you sure to delete message?");
                builder1.setCancelable(true);

                //if yes button is clicked
                builder1.setPositiveButton(
                        "Yes",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                //remove item from the list
                                message_list.remove(pos);
                                //refresh item in the list
                                adapter.notifyDataSetChanged();
                                //call saveFile function
                                saveFile();
                            }
                        });
                //if no button is clicked
                builder1.setNegativeButton(
                        "No",
                        //cancel dialog box
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                dialog.cancel();
                            }
                        });
                AlertDialog alertDelete = builder1.create();
                alertDelete.show();
                return true;
            }
        });
    }



    //function Connect
    //Description: Connect to mqtt broker
    //Parameter: None
    //Return Value: None
    private void Connect() {
        client.setCallback(new MqttCallback() {


            //callback when connection is lost
            @Override
            public void connectionLost(Throwable cause) {
                System.out.println("Connection was lost!");
                //editText.setEnabled(true);
                //switchButton.setChecked(false);
                //connectionStatus.setText("Disconnected");
                //Disconnect();

            }

            //callback when messaged is received
            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                System.out.println("Message Arrived!: " + topic + ": " + new String(message.getPayload()));
                //get time period, AM or PM
                String timePeriod = new SimpleDateFormat("a").format(Calendar.getInstance().getTime());

                //if messaged received is data
                if(topic.contains("topic/data")){
                    System.out.println("TOPIC/DATA");
                    //get message.getPayload
                    mesPayload = new String(message.getPayload());
                    //replace T to /
                    mesPayload = mesPayload.replace("T", "/");
                    String[] tokens = mesPayload.split("/");
                    getTime = tokens[2];
                    //get milliseconds up to two decimal place
                    getTime = getTime.substring(0, getTime.length() - 5);
                    //add time period to the time
                    getTime = getTime + " " +timePeriod;
                    System.out.println("getTime: " + getTime);
                    //add time in message_list

                }


                //if message received is image
                if(topic.contains("topic/image")){
                    //vibrate for 500 milliseconds
                    vibrator.vibrate(500);
                    System.out.println("MESSAGE LENGTH IN IMAGE: " + message.getPayload().length);
                    System.out.println("TOPIC/IMAGE");
                    //get message.Payload then save in byteContent variable
                    byteContent = ((message.getPayload()));
                    //decode byteContent to ByteArray then save in bmp variable
                    bmp = BitmapFactory.decodeByteArray(byteContent, 0, byteContent.length);

                    //get application context
                    ContextWrapper context = new ContextWrapper(getApplicationContext());
                    //go to directory
                    File directory = context.getDir("imageDir", Context.MODE_PRIVATE);
                    System.out.println("DIRECTORY:" + directory);

                    //save image in different file name and append timestamp
                    File file = new File(directory, "image" + getTime + ".jpg");
                    FileOutputStream fos = null;
                    try {
                        fos = new FileOutputStream(file);
                        bmp.compress(Bitmap.CompressFormat.JPEG, 90, fos);
                        fos.flush();
                        fos.close();

                    } catch (java.io.IOException e) {
                        System.out.println("Exception: " + e);
                    }
                    message_list.add(0,getTime);
                    //refresh adapter
                    adapter.notifyDataSetChanged();
                    //call saveFile function
                    saveFile();
                    //call onNotification function
                    Notification();
                }

            }

            //callback when delivery is complete
            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                System.out.println("Delivery Complete!");
            }
        });
        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setKeepAliveInterval(60);
        mqttConnectOptions.setConnectionTimeout(5);
        mqttConnectOptions.setCleanSession(true);
        mqttConnectOptions.setAutomaticReconnect(true);

        try {
            client.connect(mqttConnectOptions, null, new IMqttActionListener() {
                //connection is successful
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    System.out.println("Connection Success!");
                    try {
                        //set textview text to CONNECTED
                        connectionStatus.setText("Connected");
                        System.out.println("Subscribing to topic");
                        //subscribe to topic/data
                        client.subscribe(topicData, 0);
                        //subscribe to topic/image
                        client.subscribe(topicImage, 0);
                        //display a pop up message
                        Toast.makeText(getApplicationContext(), "Connected", Toast.LENGTH_LONG).show();
                    } catch (MqttException ex) {
                        //set switch button to false
                        switchButton.setChecked(false);
                        Toast.makeText(getApplicationContext(), "Not Connected", Toast.LENGTH_LONG).show();
                    }
                }
                //connection failed
                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    //set connection status to "Not connected"
                    connectionStatus.setText("Not connected");
                    //set switch button to false
                    switchButton.setChecked(false);
                    //call ErrorDialogBox function
                    ErrorDialogBox();
                    editText.isEnabled();
                    System.out.println("throwable: " + exception.toString());
                }
            });
        } catch (MqttException ex) {
            //call ErrorDialogBox function
            ErrorDialogBox();
            System.out.println(ex.toString());
            //set switch button to false
            switchButton.setChecked(false);
            editText.isEnabled();
            Toast.makeText(getApplicationContext(), "Not Connected", Toast.LENGTH_LONG).show();
        }
    }


    //function Disconnect
    //Description: disconnects to mqtt broker
    //Parameter: None
    //Return Value: None
    private void Disconnect(){
        if (client != null) {
            try {
                //disconnect client
                client.disconnect();
                //set connectionStatus to Disconnected
                connectionStatus.setText("Disconnected");
                //Toast.makeText(getApplicationContext(), "Disconnected", Toast.LENGTH_LONG).show();
            } catch (MqttException e) {
                e.printStackTrace();
                System.out.println("failed");
            }
        }
    }

    //function TextWatcher
    //Description: disables switch button if edit text is empty
    //Parameter: None
    //Return Value: None
    private TextWatcher loginTextWatcher = new TextWatcher() {
        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {
        }
        //on edit text change
        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            String ipAddress = editText.getText().toString().trim();
            //disable switch button if ipAddress is empty
            switchButton.setEnabled(!ipAddress.isEmpty());
            //set switch button to false
            switchButton.setChecked(false);
            //set connection status to none
            connectionStatus.setText("");
        }
        @Override
        public void afterTextChanged(Editable s) {
        }
    };


    //function Notification
    //Description: pushes notification whn alert message is received
    //Parameter: None
    //Return Value: None
    private void Notification() {
        //initialize intent to Activity_ImageView class
        final Intent intent = new Intent(MainActivity.this, Activity_ImageView.class);
        //create a key to be identified in Activity_ImageView
        intent.putExtra("key",getTime);
        //initialize MainActivity as pending intent
        PendingIntent pendingIntent = PendingIntent.getActivity(MainActivity.this, 0, intent, PendingIntent.FLAG_CANCEL_CURRENT);
        //build notification
        NotificationCompat.Builder builder = new NotificationCompat.Builder(MainActivity.this, "default")
                //set small icon
                .setSmallIcon(R.drawable.ic_message)
                //set content title
                .setContentTitle("New message received")
                //set content text
                .setContentText(getTime)
                //set content intent
                .setContentIntent(pendingIntent)
                //set auto cancel
                .setAutoCancel(true);
        //show notification
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder.setChannelId("com.example.mqttclient");
            NotificationChannel channel = new NotificationChannel(
                    "com.example.mqttclient",
                    "MQTT Client",
                    NotificationManager.IMPORTANCE_DEFAULT
            );
            if (notificationManager != null) {
                notificationManager.createNotificationChannel(channel);
            }
        }
        notificationManager.notify(0, builder.build());

    }

    //function  readFile
    //Description: read the message list saved in the textfile
    //Parameter: None
    //Return Value: None
    private void readFile() {
        //go to file directory
        File fileEvents = new File(MainActivity.this.getFilesDir() + "/text/sample");
        try {
            BufferedReader br = new BufferedReader(new FileReader(fileEvents));
            String line;
            //read contents in text file
            while ((line = br.readLine()) != null) {
                message_list.add(line);
            }
        } catch (IOException e) {
            System.out.println("Exception in reading file: "+ e);
        }
    }

    //function saveFile
    //Description: save received messages in a text file, create a text file if does not exist
    //Parameter: None
    //Return Value: None
    private void saveFile(){
        //go to file directory
        File file = new File(MainActivity.this.getFilesDir(), "text");
        //create file if it does not exist
        if (!file.exists()) {
            file.mkdir();
        }
        try {
            File gpxfile = new File(file, "sample");
            FileWriter writer = new FileWriter(gpxfile);
            //add index of message list in the text file
            for(int i=0; i<message_list.size();i++) {
                writer.write(message_list.get(i));
                writer.append("\n");
            }
            writer.flush();
            writer.close();
        } catch (Exception e) {
            Toast.makeText(getBaseContext(), e.getMessage(),
                    Toast.LENGTH_SHORT).show();
        }
    }

    //function backButtonEvent
    //Description: disconnects to mqttbroker if back button is clicked
    //Parameter: None
    //Return Value: None
    private void backButtonEvent(){

        OnBackPressedCallback callback = new OnBackPressedCallback(true /* enabled by default */) {
            @Override
            public void handleOnBackPressed() {
                //Disconnect to mqtt host
                Disconnect();
                //close the app
                MainActivity.this.finishAffinity();
            }
        };
        MainActivity.this.getOnBackPressedDispatcher().addCallback(this, callback);
    }

    //function ErrorDialogBox
    //Description: show error dialog box if mobile cannot connect to mqtt broker
    //Parameter: None
    //Return Value: None
    public void ErrorDialogBox(){
        //build error dialog box
        AlertDialog.Builder builder1 = new AlertDialog.Builder(MainActivity.this);
        //set message of dialog box
        builder1.setMessage("Cannot connect to the server");
        builder1.setCancelable(true);

        //if OK button is clicked
        builder1.setPositiveButton(
                "OK",
                //cancel dialog box
                new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        dialog.cancel();
                    }
                }
                );
        //set connection status to none
        connectionStatus.setText("");
        //enable edit text
        editText.setEnabled(true);
        AlertDialog alert11 = builder1.create();
        alert11.show();
    }
}
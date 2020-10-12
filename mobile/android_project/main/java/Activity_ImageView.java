package com.example.mqttclient;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.ContextWrapper;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;


//class Activity_ImageView
//Description: class that display image with bounding box
//      Display text
//Parameter: None
//Return: None
public class Activity_ImageView extends AppCompatActivity {
    //initialize value
    String value;
    //initialize locationView
    ImageView locationView;
    //initialize text view
    TextView textview;
    //initialize bitmap
    Bitmap bmp;

    //function onCreate
    //Description: initializes Activity_ImageView that displays image
    //Parameter: activity__image_view
    //Return Value: None
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity__image_view);

        //image view linked to the xml
        locationView = (ImageView) findViewById(R.id.imageView3);
        //text view linked to the xml
        textview = (TextView) findViewById(R.id.textView2);

        Bundle extras = getIntent().getExtras();
        if (extras != null) {
            value = extras.getString("key");
            System.out.println("VALUE: " + value);

        }
        //set text view to value
        textview.setText(value);
        //get application context
        ContextWrapper context = new ContextWrapper(getApplicationContext());
        //go to the directory where the image is saved
        File directory = context.getDir("imageDir", Context.MODE_PRIVATE);
        try {
            //get the image saved in file
            File f = new File(directory, "image"+ value+".jpg");
            bmp = BitmapFactory.decodeStream(new FileInputStream(f));

            //set the imageView with the decoded image with location
            locationView.setImageBitmap(bmp);

        } catch (FileNotFoundException e) {
            e.printStackTrace();
            System.out.println("EXCEPTION in reading file:" + e);
            Toast.makeText(getApplicationContext(), "File not found", Toast.LENGTH_LONG).show();
        }
    }
}

package com.example.appspycheat

import android.content.Intent
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.Chronometer
import android.widget.TextView
import android.widget.ThemedSpinnerAdapter

class HandActivity : AppCompatActivity(), SensorEventListener {

    private lateinit var chrono : Chronometer
    private lateinit var sensorManager: SensorManager
    private lateinit var accel : Sensor

    private lateinit var erreur_coH : TextView


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hand)

        erreur_coH = findViewById<View>(R.id.erreur_connexionH) as TextView
        optionTeteOuMain = "main"
        imageForGRPC = ""

        val butQ = findViewById<Button>(R.id.btn_quitterHa)
        butQ.setOnClickListener {
            nomReu = ""
            mailEtud =""
            optionTeteOuMain = ""
            tenteConnexion = "false"
            sensorManager.unregisterListener(this)
            chrono.stop()
            startActivity(Intent(this, AcceuilActivity::class.java));
        }

        val butS = findViewById<Button>(R.id.btn_start)
        butS.setOnClickListener {
            connectHand = "true"
            chrono = findViewById<Chronometer>(R.id.chrono)
            chrono.start()

            //on lance l'accéléromètre
            sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
            accel = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
            sensorManager.registerListener(this,accel, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    override fun onSensorChanged(event: SensorEvent?) {
        x = event!!.values[0]
        y = event.values[1]
        z = event.values[2]
        if(connexionServer() == 0){
            erreur_coH.text = "Echec de connexion au serveur, patienter"
        }
        else{
            erreur_coH.text = ""
        }
    }

    override fun onAccuracyChanged(p0: Sensor?, p1: Int) {
        return
    }
}
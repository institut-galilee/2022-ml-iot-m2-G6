package com.example.appspycheat

import android.content.Intent
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.*

/*
* Auteur de tous le fichier : Hajar BOUZIANE
* */
class HandActivity : AppCompatActivity(), SensorEventListener {
    // > Pour chronomètre
    private lateinit var chrono : Chronometer
    // > Pour l'accélléromètre
    private lateinit var sensorManager: SensorManager
    private lateinit var accel : Sensor
    // > Pour connexion serveur
    private lateinit var erreur_coH : TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hand)

        erreur_coH = findViewById<View>(R.id.erreur_connexionH) as TextView
        imageForGRPC = ""

        // Si on veut quitter la réunion
        val butQ = findViewById<Button>(R.id.btn_quitterHa)
        butQ.setOnClickListener {
            // On prévient le serveur que la réunion sur la main est fermée
            etatReu = "termine"
            connexionServer()
            // On réinitialise les variables globales pour une prochiane connexion
            nomReu = ""
            mailEtud =""
            optionTeteOuMain = ""
            etatReu = ""
            // on arrête l'accéléromètre
            sensorManager.unregisterListener(this)
            // On stop le chronomètre
            chrono.stop()
            // on est redirigé vers la page d'acceuil
            startActivity(Intent(this, AcceuilActivity::class.java));
        }

        // Si on commence la réunion sur la main
        val butS = findViewById<Button>(R.id.btn_start)
        butS.setOnClickListener {
            // on prévient le serveur que la réunion est en cours
            connectHand = "true"
            optionTeteOuMain = "main"
            etatReu = "en cours"
            // on lance le chronomètre
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
        // On envoie les valeurs de l'accéléromètre au serveur
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
    // On bloque la touche de retour en arrière du téléphone
    override fun onBackPressed() {
        Toast.makeText(this, "Appuyer sur QUITTER pour sortir de la réunion", Toast.LENGTH_SHORT).show()
    }
}
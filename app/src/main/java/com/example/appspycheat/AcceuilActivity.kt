package com.example.appspycheat

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

/*
* Auteur de tous le fichier : Hajar BOUZIANE
* */
class AcceuilActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_acceuil)

        // > Pour les Bouttons
        val butCo = findViewById<Button>(R.id.btn_connect)
        val butCr = findViewById<Button>(R.id.btn_creat)

        // > Redirection vers la page de connexion à une réunion
        butCo.setOnClickListener {
            startActivity(Intent(this, ConnexionActivity::class.java));
        }

        // > Redirection vers la page de création d'une réunion
        butCr.setOnClickListener {
            startActivity(Intent(this, InscriptionActivity::class.java));
        }
    }

}
package com.example.appspycheat

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class AcceuilActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_acceuil)

        val butCo = findViewById<Button>(R.id.btn_connect)
        val butCr = findViewById<Button>(R.id.btn_creat)

        butCo.setOnClickListener {
            startActivity(Intent(this, ConnexionActivity::class.java));
        }

        butCr.setOnClickListener {
            startActivity(Intent(this, InscriptionActivity::class.java));
        }
    }
}
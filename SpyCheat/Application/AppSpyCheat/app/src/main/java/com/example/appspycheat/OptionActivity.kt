package com.example.appspycheat

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class OptionActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_option)

        val butT = findViewById<Button>(R.id.btn_tete)
        val butH = findViewById<Button>(R.id.btn_main)
        val butQO = findViewById<Button>(R.id.btn_quitterO)

        butT.setOnClickListener {
            startActivity(Intent(this, HeadActivity::class.java));
        }

        butH.setOnClickListener {
            startActivity(Intent(this, HandActivity::class.java));
        }

        butQO.setOnClickListener {
            nomReu = ""
            mailEtud =""
            startActivity(Intent(this, HandActivity::class.java));
        }
    }
}
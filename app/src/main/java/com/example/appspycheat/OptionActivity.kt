package com.example.appspycheat

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
/*
* Auteur de tous le fichier : Hajar BOUZIANE
* */
class OptionActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_option)

        // > Bouttons pour l'option "tete"
        val butT = findViewById<Button>(R.id.btn_tete)
        // > Bouttons pour l'option "main"
        val butH = findViewById<Button>(R.id.btn_main)
        // > Bouttons pour revenir à la page de connexion
        val butQO = findViewById<Button>(R.id.btn_quitterO)

        // L'utilisateur veut passer en mode "tete"
        butT.setOnClickListener {
            // on envoie l'information au serveur (option tete)
            optionTeteOuMain = "tete"
            // On vérifie que l'envoie c'est bien passé
            if(connexionServer() == 0){
                Toast.makeText(this,
                    "Connexion au serveur perdu",
                    Toast.LENGTH_SHORT).show()
            }
            else{
                // si l'utilisateur c'est déjà connecté sur la tête dans cette réunion alors il ne peux plus y accéder
                if(tenteConnexion == "fini"){
                    Toast.makeText(this,
                        "Vous avez déjà participé à la réunion avec l\'appareil sur la tête",
                        Toast.LENGTH_SHORT).show()
                    // on réinitialise les variables globales
                    tenteConnexion = "false"
                    optionTeteOuMain = ""
                }
                else{
                    // si l'utilisateur ne sait jamais connecté sur la tête dans cette réunion alors il est redirigé vers une nouvelle page
                    startActivity(Intent(this, HeadActivity::class.java));
                }
            }
        }

        // Même raisonnement que pour le précédent bouton mais avec la main
        butH.setOnClickListener {
            optionTeteOuMain = "main"
            if(connexionServer() == 0){
                Toast.makeText(this,
                    "Connexion au serveur perdu",
                    Toast.LENGTH_SHORT).show()
            }else{
                if(tenteConnexion == "fini"){
                    Toast.makeText(this,
                        "Vous avez déjà participé à la réunion avec l\'appareil sur la main",
                        Toast.LENGTH_SHORT).show()
                    tenteConnexion = "false"
                    optionTeteOuMain = ""
                }
                else{
                    startActivity(Intent(this, HandActivity::class.java));
                }
            }
        }

        // bouton pour quitter la page
        butQO.setOnClickListener {
            // on réinitialise les variables globales
            nomReu = ""
            mailEtud =""
            optionTeteOuMain = ""
            tenteConnexion = "false"
            connectAuto = "false"
            // on est redirigé vers la page de connexion
            startActivity(Intent(this, ConnexionActivity::class.java));
        }
    }

    //on bloque la touche de retour en arrière du téléphone
    override fun onBackPressed() {
        Toast.makeText(this, "Appuyer sur QUITTER pour sortir de la réunion", Toast.LENGTH_SHORT).show()
    }
}
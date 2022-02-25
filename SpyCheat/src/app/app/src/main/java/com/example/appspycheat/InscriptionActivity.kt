package com.example.appspycheat

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
/*
* Auteur de tous le fichier : Hajar BOUZIANE
* */
class InscriptionActivity : AppCompatActivity() {
    // > pour envoyer le nom de la réunion et l'adresse mail au serveur
    private lateinit var nomReunion: EditText
    private lateinit var mailUser: EditText
    // > GRPC
    private lateinit var errConnexionI : TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_inscription)

        // On récupère le nom de la réunion
        nomReunion = findViewById<View>(R.id.reu_edit_text) as EditText
        // On récupère le mail de l'utilisateur
        mailUser = findViewById<View>(R.id.mail_edit_text) as EditText
        //Emplacement du message d'erreur si la connexion est perdu
        errConnexionI = findViewById<View>(R.id.erreur_connexionI) as TextView

        // BOUTON ENVOYER
        val butE = findViewById<Button>(R.id.envoyerU)
        butE.setOnClickListener {
            // on garde en mémoire le nom de la réunion et l'adresse mail
            nomReu = nomReunion.text.toString()
            mailEtud = mailUser.text.toString()

            //On test la connexion et on envoie l'adresse et le mail au serveur
            if(connexionServer() == 1) {
                // on rénitialise les variables global pour une prochaine connexion
                tenteConnexion = "false"
                errConnexionI.text = " "
            }
            else {
                //Connexion échouée : on affiche le message d'erreur
                errConnexionI.text = "Connexion au serveur Perdu"
            }
        }

        // BOUTON QUITTER
        val butQ = findViewById<Button>(R.id.quitterI)
        butQ.setOnClickListener {
            // on rénitialise les variables global pour une prochaine connexion
            nomReu = ""
            mailEtud = ""
            startActivity(Intent(this, AcceuilActivity::class.java));
        }
    }
}
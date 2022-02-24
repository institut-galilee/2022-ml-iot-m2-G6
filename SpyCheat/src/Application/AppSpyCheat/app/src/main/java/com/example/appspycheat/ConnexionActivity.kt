package com.example.appspycheat

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView

class ConnexionActivity : AppCompatActivity() {
    // > Connexion d'un utilisateur
    private lateinit var nomReunionC: EditText
    private lateinit var mailUserC: EditText
    // > GRPC
    private lateinit var errConnexionC : TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_connexion)

        // On récupère le nom de la réunion saisit par l'utilisateur
        nomReunionC = findViewById<View>(R.id.nomR_connect) as EditText
        // On récupère le mail sasit par l'utilisateur
        mailUserC = findViewById<View>(R.id.mail_connect) as EditText
        //Emplacement du message d'erreur si la connexion est perdu
        errConnexionC = findViewById<View>(R.id.erreur_connexionC) as TextView


        val butV = findViewById<Button>(R.id.validated_button)
        butV.setOnClickListener {
            nomReu = nomReunionC.text.toString()
            mailEtud = mailUserC.text.toString()
            //On dit au serveur qu'il s'agit d'une tentative de connexionIl s'agit d'une tentative de connexion
            tenteConnexion = "true"
            println(host + " " + port)
            if(connexionServer() == 1) {
                errConnexionC.text = " "
                //On attend la validation du serveur
                if(connectAuto == "accepte"){
                    startActivity(Intent(this, OptionActivity::class.java));
                }
                else{
                    errConnexionC.text = "Reunion et/ou adresse mail incorect(s)"
                }
                //On remet à false pour les prochaines tentative de connexion
                tenteConnexion = "false"
            }
            else {
                //Il ne s'agit d'une tentative de connexion mais qui a échoué car la connexion au serveur a échoué
                tenteConnexion = "false"
                //Connexion échouée : on affiche le message d'erreur
                errConnexionC.text = "Connexion au serveur Perdu"
            }
        }
    }
}
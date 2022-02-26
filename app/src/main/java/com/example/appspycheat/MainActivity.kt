package com.example.appspycheat

import android.content.Intent
import android.content.pm.PackageManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.appspycheat.databinding.ActivityMainBinding

/*
* Source :
* Aide caméraX (Vidéo Youtube) -> https://www.youtube.com/watch?v=HjXJh_vHXFs
 */
class MainActivity : AppCompatActivity() {
    // > Pour CAMERAX
    private lateinit var binding : ActivityMainBinding
    // > Pour GRPC
    private lateinit var hostEdit: EditText
    private lateinit var portEdit: EditText
    private lateinit var errConnexion : TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        /* ********************** Vidéo Youtube ************************ */
        /* ***************** PERMISSION CAMERA DEBUT ******************* */
        if (allPermissionGranted()) {
            Toast.makeText(this,
                "Permission Caméra Accordée",
                Toast.LENGTH_SHORT).show()
        }else{
            ActivityCompat.requestPermissions(
                this, Constants.REQUIRED_PERMISSIONS,
                Constants.REQUEST_CODE_PERMISSION)
        }
        /* ***************** PERMISSION CAMERA FIN ********************* */
        /* ************************************************************* */


        /* **************** Auteur : Hajar BOUZIANE ********************* */
        /* **************** CONNEXION SERVEUR DEBUT ********************* */
        //IP saisit par l'utilisateur
        hostEdit = findViewById<View>(R.id.host_edit_text) as EditText
        //Port saisit par l'utilisateur
        portEdit = findViewById<View>(R.id.port_edit_text) as EditText
        //Emplacement du message d'échec à la connexion au serveur
        errConnexion = findViewById<View>(R.id.erreur_connexion) as TextView

        //Si on clique sur le bouton "CONNEXION AU SERVEUR"
        val butter = findViewById<Button>(R.id.send_button)
        butter.setOnClickListener{
            // On garde en mémoire l'IP et le Port
            host = hostEdit.text.toString()
            port = portEdit.text.toString()

            //On test la connexion
            if(connexionServer() == 1) {
                // Connexion succès : on retire le message d'erreur si il était affiché
                errConnexion.text = " "
                // On change de page
                val intentHe = Intent(this, AcceuilActivity::class.java)
                startActivity(intentHe)
            }
            else {
                //Connexion échouée : on affiche le message d'erreur
                errConnexion.text = "Adresse IP et/ou Port incorrect"
            }
        }
        /* ***************** CONNEXION SERVEUR FIN ********************** */
        /* ************************************************************** */
    }

    /* ********************** Vidéo Youtube ************************ */
    /* ***************** PERMISSION CAMERA DEBUT ******************* */
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if(requestCode == Constants.REQUEST_CODE_PERMISSION){
            if(allPermissionGranted()){
                // On ne fait rien
            }else{
                Toast.makeText(this,
                    "Permission Caméra NON Accordée.",
                    Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }

    private fun allPermissionGranted() =
        Constants.REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(
                baseContext, it
            ) == PackageManager.PERMISSION_GRANTED
        }
    /* ***************** PERMISSION CAMERA FIN ********************* */
    /* ************************************************************* */
}
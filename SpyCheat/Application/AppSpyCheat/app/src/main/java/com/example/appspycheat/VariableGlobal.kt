package com.example.appspycheat

import android.text.TextUtils
import com.examples.appspycheat.Envoie
import com.examples.appspycheat.EnvoieServiceGrpc
import com.examples.appspycheat.GetEnvoieRequest
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import java.util.concurrent.TimeUnit

// > GRPC
var host : String = ""
var port : String = ""

// > Membres de la reunion
var nomReu: String = ""
var mailEtud: String = ""

// > Connexion autorisée
var connectAuto : String = "false"

// > Option
var dansOptionTete: String = "false"
var dansOptionMain: String = "true"
var optionTeteOuMain: String = ""
var connectHand : String = "false"
var connectHead : String = "false"

// > true pour reunion en cours/termine sinon false
var etatReu: String = "false"

// > CameraX
var imageForGRPC : String = ""

// > Accéléromètre
var x = 0f
var y = 0f
var z = 0f

var tenteConnexion : String ="false"

/*
* Auteur : Hajar BOUZIANE
* Aide : GRPC Basic Tutoriel (Kotlin) -> https://grpc.io/docs/languages/kotlin/basics/
*
* Fonction qui va permettre a notre application de ce connecté au serveur et de lui envoyer
* des information.
* Si la connexion a échoué (adresse IP et/ou port) incorrect alors la fonction renvoie 0
* Sinon elle renvoie 1
* */
fun connexionServer() : Int {
    println(host + " " + port)
    try{
        // Connexion client -> serveur après avoir récupéré l'IP et le port
        val channel: ManagedChannel
        val newport = if (TextUtils.isEmpty(port)) 50051 else Integer.valueOf(port)
        channel = ManagedChannelBuilder
            .forAddress(host, newport)
            .usePlaintext()
            .build()

        // Si la connexion est un succès, on envoie nos données au serveur
        val stub: EnvoieServiceGrpc.EnvoieServiceBlockingStub = EnvoieServiceGrpc.newBlockingStub(channel).withDeadlineAfter(2,TimeUnit.SECONDS)
        val request: GetEnvoieRequest = GetEnvoieRequest.newBuilder()
            .setNomReunion(nomReu)
            .setMailEtudiant(mailEtud)
            .setTeteOuMain(optionTeteOuMain)
            .setEtatReunion(etatReu)
            .setImage(imageForGRPC)
            .setX(x)
            .setY(y)
            .setZ(z)
            .setTentaConnec(tenteConnexion)
            .build()
        var reply : Envoie = stub.getEnvoie(request)
        if(reply.tentaConnec == "accepte"){
            connectAuto = "accepte"
        }
        else{
            connectAuto = "refuse"
        }
        //Une fois les données envoyé, on ferme le channel
        channel.shutdown()
    }catch (e:Exception){
        return 0
    }
    return 1
}
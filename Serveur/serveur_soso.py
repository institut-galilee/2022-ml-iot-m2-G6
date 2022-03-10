# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC acc.Greeter server."""

from concurrent import futures
import logging
# Pour GRPC
import grpc
import envoie_pb2
import envoie_pb2_grpc
# Pour String -> image
import base64
# Pour écrire dans les fichiers csv
import csv
import os
import pandas as pd
# Pour les coordonnées
import numpy as np
# Pour l'enregistrement vocal
import sounddevice as sd
import wavio as wv
import threading
import wave
# import the necessary packages
import argparse
import cv2
import datetime


# liste pour récupèrer les n premiers coordonnées
calibrageL = []
# liste stockants les coordonnées calibrées
moyenne_calibrage = []
# indice d'itération pour récupérer les n premiers coordonées
index = 0

enregistrement_en_cours = False


class Greeter(envoie_pb2_grpc.EnvoieServiceServicer):

    def GetEnvoie(self, request, context):
        global enregistrement_en_cours

        # On récupère l'image renvoyé par l'application
        # String -> image
        if(request.image != ""):
            base64_to_image(str.encode(request.image))
        
        # On traite les inscriptions ou les connexions de candidats
        if(request.teteOuMain == ""):
            #si le nom de la reunion ET le mail n'est pas Vide
            if(request.nomReunion != "" and request.mailEtudiant !=""):
                if(request.tentaConnec == "true"):
                    if(verifCandidat(request.nomReunion, request.mailEtudiant) == False):
                        request.tentaConnec="refuse"
                        print("Connexion REFUSEE de", request.mailEtudiant, "pour la réunion", request.nomReunion)
                    else:
                        request.tentaConnec="accepte"
                        print("Connexion ACCEPTEE de", request.mailEtudiant, "pour la réunion", request.nomReunion)
                else:
                    if(verifCandidat(request.nomReunion, request.mailEtudiant) == False):
                        ajoutCandidat(request.nomReunion, request.mailEtudiant)
                        print("Adresse :", request.mailEtudiant , "ajouté à la réunion",  request.nomReunion)
                    else :
                        print("Adresse :", request.mailEtudiant , "existe déjà dans la réunion",  request.nomReunion)
            
        # On traite les réunions lancées depuis la tête ou depuis la main
        else:
            # **************************************************************************************************************************************************
            # *************************************************** DEBUT TRAITEMENT REUNION DEPUIS < MAIN > *****************************************************
            if(request.teteOuMain == "main"):
                # si le candidat veut se connecter à une réunion avec la main, MAIS que cette même réunion est déjà marqué comme TERMINE
                # alors le serveur envoie un message au client (application)
                if(encours_ou_termine('InventaireMainReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Main', "termine") == 1):
                        request.tentaConnec = "fini"
                        """
                        print(" nomReunion = ", request.nomReunion, 
                        " mailEtudiant = ", request.mailEtudiant, 
                        " teteOuMain = ", request.teteOuMain, 
                        " etatReunion = ", request.etatReunion,
                        " image = ", request.image,
                        " x = ", request.x,
                        " y = ", request.y,
                        " z = ", request.z,
                        " tentaConnec = ", request.tentaConnec)
                        """
                # si la réunion est en cours alors on commence par calibrer les valeurs de l'accéléromètre en début de réunion
                # Puis on affiche les mouvements de la main [ doit être améliorée ]
                elif(request.etatReunion == "en cours") :       
                    print("\n> La réunion [", request.nomReunion, "] du candidat ", request.mailEtudiant, "est EN COURS")  
                    """    
                    print("EN COURS ....")          
                    print(" x = ", request.x,
                    " y = ", request.y,
                    " z = ", request.z)
                    """

                    # on calibre les valeurs de l'accéléromètre
                    calibrage(request.x, request.y, request.z, 10)
                    # on inscrit dans le fihcier excel que la réunion est en cours sur la main
                    if(encours_ou_termine('InventaireMainReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Main', request.etatReunion) < 1):
                        inventaire('InventaireMainReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Main', request.etatReunion)

                # si la réunion est terminé, on le marque dans le fichier excel
                elif(request.etatReunion == "termine") :
                    print("\n>", request.mailEtudiant, " a TERMINE la réunion [", request.nomReunion, "]") 
                    """
                    print("TERMINEE")
                    print(" nomReunion = ", request.nomReunion, 
                    " mailEtudiant = ", request.mailEtudiant, 
                    " teteOuMain = ", request.teteOuMain, 
                    " etatReunion = ", request.etatReunion,
                    " image = ", request.image,
                    " x = ", request.x,
                    " y = ", request.y,
                    " z = ", request.z,
                    " tentaConnec = ", request.tentaConnec)
                    """
                    inventaire('InventaireMainReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Main', request.etatReunion)
            # *************************************************** FIN TRAITEMENT REUNION DEPUIS < MAIN > *******************************************************
            # **************************************************************************************************************************************************
            


            # **************************************************************************************************************************************************
            # **************************************************** DEBUT TRAITEMENT REUNION DEPUIS < TETE > ****************************************************
            else:
                # si le candidat veut se connecter à une réunion avec la tête, MAIS que cette même réunion est déjà marqué comme TERMINE
                # alors le serveur envoie un message au client (application)
                if(encours_ou_termine('InventaireTeteReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Tete', "termine") == 1):
                        request.tentaConnec = "fini"
                        """
                        print(" nomReunion = ", request.nomReunion, 
                        " mailEtudiant = ", request.mailEtudiant, 
                        " teteOuMain = ", request.teteOuMain, 
                        " etatReunion = ", request.etatReunion,
                        " image = ", request.image,
                        " x = ", request.x,
                        " y = ", request.y,
                        " z = ", request.z,
                        " tentaConnec = ", request.tentaConnec)
                        """
            
                # si la réunion est en cours alors on commence par calibrer les valeurs de l'accéléromètre en début de réunion
                # Puis on affiche les mouvements de la tête (Gauche, droite, Haut, Bas)
                elif(request.etatReunion == "en cours") : 
                    print("\n> La réunion [", request.nomReunion, "] du candidat ", request.mailEtudiant, "est EN COURS")    
                    """  
                    print("EN COURS ....")          
                    print(" x = ", request.x,
                    " y = ", request.y,
                    " z = ", request.z)
                    """
                    #vocal.record()
                    if(enregistrement_en_cours == False):
                        record()
                        
                    # on calibre les valeurs de l'accéléromètre
                    calibrage(request.x, request.y, request.z, 5)
                    # on inscrit dans le fihcier excel que la réunion est en cours sur la tête
                    if(encours_ou_termine('InventaireTeteReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Tete', request.etatReunion) < 1):
                        inventaire('InventaireTeteReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Tete', request.etatReunion)

                # si la réunion est terminé, on le marque dans le fichier excel
                elif(request.etatReunion == "termine") : 
                    print("\n>", request.mailEtudiant, " a TERMINE la réunion [", request.nomReunion, "]")


                    
                    """
                    print(" nomReunion = ", request.nomReunion, 
                    " mailEtudiant = ", request.mailEtudiant, 
                    " teteOuMain = ", request.teteOuMain, 
                    " etatReunion = ", request.etatReunion,
                    " image = ", request.image,
                    " x = ", request.x,
                    " y = ", request.y,
                    " z = ", request.z,
                    " tentaConnec = ", request.tentaConnec)
                    """
                    inventaire('InventaireTeteReunionEtCandidats.csv', request.nomReunion, request.mailEtudiant, 'Statut_Reunion_Tete', request.etatReunion)
            # **************************************************** FIN TRAITEMENT REUNION DEPUIS < TETE > ******************************************************
            # **************************************************************************************************************************************************
        
        # Message que le serveur envoie à l'application
        return envoie_pb2.Envoie(nomReunion = request.nomReunion, 
                                 mailEtudiant = request.mailEtudiant, 
                                 teteOuMain = request.teteOuMain, 
                                 etatReunion = request.etatReunion,
                                 image = request.image,
                                 x = request.x,
                                 y = request.y,
                                 z = request.z,
                                 tentaConnec = request.tentaConnec)
                          
"""
    Fonction qui transforme une chaine de caractère en image

    @Param :
        img_data      La chaine de caractère à transformer en image 
"""
def base64_to_image (img_data) :
    name_file = "image.jpg"

    with open(name_file, "wb") as fh:
        fh.write( base64.decodebytes(img_data))

    if(os.path.exists('image.jpg')):

        '''
            Analyse de l'image dans le fichier Objects_Detection
            Ce bloc de code provient en majeure partie du lien github suivant :
            https://github.com/KingArnaiz/Object-Detection-Tutorial/blob/master/deep_learning_object_detection.py

            La traduction des classes vient de ce site qui utilise le même procédé :
            https://www.aranacorp.com/fr/reconnaissance-dobjet-avec-python/#:~:text=Object%20list%20init-,CLASSES,-%3D%20%5B%22arriere%2Dplan%22%2C%20%22avion

            Le code suivant a été modifié pour qu'au lancement du serveur il n'y ait pas d'arguments à donner (image, model et prototxt)
        ''' 
        #########################################################################################

        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--image", default = 'image.jpg',
            help="path to input image")
        ap.add_argument("-p", "--prototxt", default = 'MobileNetSSD_deploy.prototxt.txt',
            help="path to Caffe 'deploy' prototxt file")
        ap.add_argument("-m", "--model", default = 'MobileNetSSD_deploy.caffemodel',
            help="path to Caffe pre-trained model")
        ap.add_argument("-c", "--confidence", type=float, default=0.2,
            help="minimum probability to filter weak detections")
        args = vars(ap.parse_args())

        # initialize the list of class labels MobileNet SSD was trained to
        # detect, then generate a set of bounding box colors for each class
        CLASSES = ["arriere-plan", "avion", "velo", "oiseau", "bateau",
            "bouteille", "autobus", "voiture", "chat", "chaise", "vache", "table",
            "chien", "cheval", "moto", "personne", "plante en pot", "mouton",
            "sofa", "train", "moniteur"]
        COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

        # load our serialized model from disk
        # print("[INFO] loading model...")
        net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

        # load the input image and construct an input blob for the image
        # by resizing to a fixed 300x300 pixels and then normalizing it
        # (note: normalization is done via the authors of the MobileNet SSD
        # implementation)
        image = cv2.imread(args["image"])
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        # print("[INFO] computing object detections...")
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]
            string = "tentative possible de triche"

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the `detections`,
                # then compute the (x, y)-coordinates of the bounding box for
                # the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # display the prediction
                label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                # print("[INFO] {}".format(label))
                cv2.rectangle(image, (startX, startY), (endX, endY),
                    COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(image, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                # On archive tout objet ou peronne reconnu avec la date dans ce fichier csv, le lien vers la source :
                # https://github.com/augmentedstartups/Face-Recogntion-PyQt/blob/master/Face_Detection_PyQt_base/out_window.py#:~:text=with%20open(%27Attendance.csv%27%2C%20%27a%27)%20as%20f%3A
                with open('Objects_Detection.csv', 'a') as f:
                    # On met tous les labels reconnus dans l'image dans un fichier csv avec la date et l'heure 
                    date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                    f.writelines(f'\n{label},{date_time_string}')
                    # Si une personne est détectée alors on affcihe un message pour la tentative de triche
                    if label.find("personne") >= 0:
                        f.writelines(f'\n{string},{date_time_string}')
        # show the output image
        # cv2.imshow("Output", image)
        cv2.waitKey(0)

        #########################################################################################

"""
    Fonction qui ajoute un le couple (reunion, adresse mail du candidat) dans un fichier excel

    @Param:
        reunion     Le nom de la réunion
        mail        Adresse mail du candidat ajouté à la réunion
"""
def ajoutCandidat(reunion, mail) :
    # Nom du fichier qui va contenir les données
    fileName = 'ReunionEtCandidats.csv'
    # Si le fichier n'existe pas, on isnère la première données avec le nom des colonnes (header = True)
    if(not os.path.exists(fileName)):
        # ligne a ajouter au fichier csv
        donnee = {'Nom_Reunion': [reunion], 'Mail_Candidat': [mail]}
        # insertion des donnees dans les bonnes colonnes
        df = pd.DataFrame(donnee, columns= ['Nom_Reunion', 'Mail_Candidat'])
        # ecriture (en ajout) des données dans le fichier ReunionEtCandidats.csv
        export_csv = df.to_csv (fileName, mode='a', index = None, header=True, encoding='utf-8', sep=';')
    # Sinon on insère les données sans le nom des colonnes (hearder=False)
    else :
        donnee = {'Nom_Reunion': [reunion],'Mail_Candidat': [mail]}
        df = pd.DataFrame(donnee, columns= ['Nom_Reunion', 'Mail_Candidat'])
        export_csv = df.to_csv (fileName, mode='a', index = None, header=False, encoding='utf-8', sep=';')

"""
    Fonction qui remplie un fichier excel pour la Main et pour la tête
    Chaque ligne inséré sera composé du (nom de la réunion, mail du candidar, réunion en cours ou/et terminé)

    @Param :
        fileName    Nom du fichier excel où on va écrire (fichier pour la tête ou pour la main)
        reunion     Nom de la réunion
        mail        Adresse mail du candidat
        colonne     Nom de la colonne (tête ou main)
        etatReu     Soit 'en cours' soit 'terminée'
"""
def inventaire(fileName, reunion, mail, colonne, etatReu):
    # Si le fichier n'existe pas, on isnère la première données avec le nom des colonnes (header = True)
    if(not os.path.exists(fileName)):
        # ligne a ajouter au fichier csv
        donnee = {'Nom_Reunion': [reunion], 'Mail_Candidat': [mail], colonne : [etatReu]}
        # insertion des donnees dans les bonnes colonnes
        df = pd.DataFrame(donnee, columns= ['Nom_Reunion', 'Mail_Candidat', colonne])
        # ecriture (en ajout) des données dans le fichier ReunionEtCandidats.csv
        export_csv = df.to_csv (fileName, mode='a', index = None, header=True, encoding='utf-8', sep=';')
    # Sinon on insère les données sans le nom des colonnes (hearder=False)
    else :
        donnee = {'Nom_Reunion': [reunion],'Mail_Candidat': [mail], colonne : [etatReu]}
        df = pd.DataFrame(donnee, columns= ['Nom_Reunion', 'Mail_Candidat', colonne])
        export_csv = df.to_csv (fileName, mode='a', index = None, header=False, encoding='utf-8', sep=';')

"""
    Fonction qui permet de savoir si une réunion est en cours ou terminé pour une réunion et une adresse mail précise
    @Param
        fileName    Nom du fichier pour effectuer la recherche sur l'état de la réunion courant
        reunion     Nom de la réunion
        mail        Adresse mail du candidat
        colonne     Nom de la colonne (tête ou main)
        statut      Soit 'en cours' soit 'terminée'
    @Return
        le nombre de fois qu'est écrit une réunion 'en cours' et/ou terminé
"""
def encours_ou_termine(fileName, reunion, mail, colonne, statut):
    if(not os.path.exists(fileName)):
        return 0
    data = pd.read_csv(fileName, sep=';')

    reunion = data[data['Nom_Reunion'] == reunion]
    mail = reunion[reunion['Mail_Candidat'] == mail]
    statut = mail[mail[colonne] == statut]
    return len(statut)

"""
    Fonction qui vérifie si un candidat est inscrit à une réunion
    @Param
        reunion     Nom de la réunion
        mail        Adresse mail du candidat
    @Return
        Renvoie True si le candidat est inscrit à la réunion sinon False
"""
def verifCandidat(reunion, mail):
    # fichier qui contient la liste des réunions et candidats
    fileName = "ReunionEtCandidats.csv"

    if(not os.path.exists(fileName)):
        return False
    # on ouvre le fichier en délimitant les colonnes ';'
    data = pd.read_csv(fileName, sep=';')
    # On récupère toute les lignes correspondant à la réunion courante
    liste_reunion = np.array(data[data['Nom_Reunion'] == reunion])
    # On verifie si le mail est inscrit dans la reunion
    return mail in liste_reunion[:,1]

"""
    Fonction qui permet de calibrer les corrdonnées de l'accéléromètre
    @Param
        x y z       Coordonnées de l'accéléromètre
        nb_ite      Nombre de coordonnées que l'on va utilisé pour calibrer l'accéléromètre
"""
def calibrage(x, y ,z ,nb_ite):
    # variable global correspondant aux nombre de coordonnées que l'on va utilisé pour calibrer l'accéléromètre
    global index
    # variable global correspondant à la moyenne des x puis des y et enfin des z (serviront de repère pour les mouvements)
    global moyenne_calibrage
    if(index < nb_ite):
        calibrageL.append([x,y,z])
        moyenne_calibrage = np.mean(calibrageL, axis=0).copy()
        index = index + 1
    else:
        # quand on lève la tête z devient de plus en plus grand (rapidement)
        if( z > 0 and np.abs(z - moyenne_calibrage[2]) > 2):
            print(" # Mouvement vers le HAUT détecté !")
        # quand on baisse la tête z devient de plus en plus petit (rapidement)
        if( z < 0 and np.abs(z - moyenne_calibrage[2]) > 2):
            print(" # Mouvement vers le BAS détecté !")
        # quand on tourne la tête à gauche, x devient de plus en plus grand (lentement)
        if(x > 0 and np.abs(z - moyenne_calibrage[2]) < 0.3):
            print(" # Mouvement vers la GAUCHE détecté !")
        if(x > 0 and np.abs(z - moyenne_calibrage[2]) > 0.5):
            print(" # Mouvement vers la DROITE détecté !")
            
        """
        if(x > 0 and np.abs(x - moyenne_calibrage[0]) > 0.5):
            print(" # Mouvement vers la GAUCHE détecté !")
        # quand on tourne la tête à droite, x devient de plus en plus petit (lentement)
        if(x < 0 and np.abs(x - moyenne_calibrage[0]) > 0.5):
            print(" # Mouvement vers la DROITE détecté !")
        """

"""
    Aide : https://fr.acervolima.com/creer-un-enregistreur-vocal-a-laide-de-python/#:~:text=Utilisation%20de%20wavio%3A
    
    Fonction qui lance un enregistrement pendant 5 secondes et le stocke dans un fichier wav
    Si l'enregistrement est déjà en cours, on ne le lance pas.
    Sinon on lance l'enregistrement.

    Comme c'est des enregistrement de 5 secondes, on concatène le précédent enregistrement avec le nouveau pour former un 
    enregistrement qui sera aussi long que la durée de la réunion
"""
def record():
    global enregistrement_en_cours
    freq = 44100
    duration = 5
    # Si un premier en engistrement à été fais, on crée un fichier temporaire pour stocker les nouvelles 5 secondes d'enregistrement
    #       et on concataine cet enregistrement avec le précédent
    filename = "exam_recording.wav"
    if(os.path.exists(filename)):
        # Début de l'enregistrement
        enregistrement_en_cours = True

        # Enregistrement du n-ième enregistrement
        filename = "exam_recording2.wav"
        print("> Start Recording")
        recording = sd.rec(int(duration * freq), samplerate = freq, channels=2)
        sd.wait()
        wv.write(filename, recording, freq, sampwidth=2)
        print("> Finished recording")

        # Concaténation de cet enregistrement avec le précédent
        infiles = ["exam_recording.wav", "exam_recording2.wav"]
        outfile = "exam_recording.wav"

        data= []
        for infile in infiles:
            w = wave.open(infile, 'rb')
            data.append( [w.getparams(), w.readframes(w.getnframes())] )
            w.close()

        output = wave.open(outfile, 'wb')
        output.setparams(data[0][0])
        output.writeframes(data[0][1])
        output.writeframes(data[1][1])
        output.close()
        # Fin de l'enregistrement
        enregistrement_en_cours = False

    # Sinon on crée un fichier pour notre premier enregistrement
    else:
        # L'enregistrement est en cours
        enregistrement_en_cours = True
        print("> Start Recording")
        recording = sd.rec(int(duration * freq), samplerate = freq, channels=2)
        sd.wait()
        wv.write(filename, recording, freq, sampwidth=2)
        print("> Finished recording")
        # L'enregistrement est terminé
        enregistrement_en_cours = False
   


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    envoie_pb2_grpc.add_EnvoieServiceServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()

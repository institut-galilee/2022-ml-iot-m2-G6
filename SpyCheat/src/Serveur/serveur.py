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

import grpc
import envoie_pb2
import envoie_pb2_grpc
import base64
import csv
import os
import pandas as pd
import numpy as np

class Greeter(envoie_pb2_grpc.EnvoieServiceServicer):

    def GetEnvoie(self, request, context):
        if(request.image != ""):
            base64_to_image(str.encode(request.image), 0)
            
        print(" nomReunion = ", request.nomReunion, 
              " mailEtudiant = ", request.mailEtudiant, 
              " teteOuMain = ", request.teteOuMain, 
              " etatReunion = ", request.etatReunion,
              " image = ", request.image,
              " x = ", request.x,
              " y = ", request.y,
              " z = ", request.z,
              " tentaConnec = ", request.tentaConnec)


        if(request.teteOuMain == ""):
            #si le nom de la reunion ET le mail n'est pas Vide
            if(request.nomReunion != "" and request.mailEtudiant !=""):
                if(request.tentaConnec == "true"):
                    if(verifCandidat(request.nomReunion, request.mailEtudiant) == False):
                        request.tentaConnec="refuse"
                    else:
                        request.tentaConnec="accepte"
                else:
                    if(verifCandidat(request.nomReunion, request.mailEtudiant) == False):
                        ajoutCandidat(request.nomReunion, request.mailEtudiant)
        else:
            print("helloo")


        """
        # si on a donne un nom a la reunion ET une adresse mail
        if(request.nomReunion != "" and request.mailEtudiant !=""):
            # on verifie que le couple n'est pas déjà inscrit dans le fichier
            if(verifCandidat(request.nomReunion, request.mailEtudiant) == False):
                # on l'ajoute dans le fichier
                ajoutCandidat(request.nomReunion, request.mailEtudiant)
            # else : le serveur envoie au client qu'il existe et qu'il peut se connecter (tester sur le fichier client)
            else :
                print("connexion autorisé pour " + request.nomReunion + " " + request.mailEtudiant)
        """

        return envoie_pb2.Envoie(nomReunion = request.nomReunion, 
                                 mailEtudiant = request.mailEtudiant, 
                                 teteOuMain = request.teteOuMain, 
                                 etatReunion = request.etatReunion,
                                 image = request.image,
                                 x = request.x,
                                 y = request.y,
                                 z = request.z,
                                 tentaConnec = request.tentaConnec)

def base64_to_image (img_data, i) :
    name_file = "imageToSave" + str(i) + ".jpg"

    with open(name_file, "wb") as fh:
        fh.write( base64.decodebytes(img_data) )

def ajoutCandidat(reunion, mail) :
    # Nom du fichier qui va contenir les données
    fileName = 'ReunionEtCandidats.csv'
    # Si le fichier n'existe pas, on isnère la première données avec le nom des colonnes (header = True)
    if(not os.path.exists(fileName)):
        # ligne a ajouter au fichier csv
        donnee = {'Nom_Reunion': [reunion],'Mail_Candidat': [mail]}
        # insertion des donnees dans les bonnes colonnes
        df = pd.DataFrame(donnee, columns= ['Nom_Reunion', 'Mail_Candidat'])
        # ecriture (en ajout) des données dans le fichier ReunionEtCandidats.csv
        export_csv = df.to_csv (fileName, mode='a', index = None, header=True, encoding='utf-8', sep=';')
    # Sinon on insère les données sans le nom des colonnes (hearder=False)
    else :
        donnee = {'Nom_Reunion': [reunion],'Mail_Candidat': [mail]}
        df = pd.DataFrame(donnee, columns= ['Nom_Reunion', 'Mail_Candidat'])
        export_csv = df.to_csv (fileName, mode='a', index = None, header=False, encoding='utf-8', sep=';')

    
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


   

    


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    envoie_pb2_grpc.add_EnvoieServiceServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()

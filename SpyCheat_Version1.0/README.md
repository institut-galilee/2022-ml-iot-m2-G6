# 2022 - SpyCheat

## Présentation

SpyCheat a été conçue par **Sohayla RABHI** et **Hajar BOUZIANE** dans le but de surveiller des candidats qui passent un examen. Il est composé d'une **application** créé par Hajar BOUZIANE et d'un **serveur** mis en place par Sohayla RABHI.

L'application joue le rôle d'un client et permet à un utilisateur de :

- **créer une réunion** en spécifiant les adresses mails des utilisateurs qui auront accès à celle-ci,
- **se connecter** pour commencer l'examen. Dans ce cas, il doit choisir l'emplacement de l'appareil où l'application a été installé (**tête** et/ou **main**).

Le serveur quant à lui, récolte les données envoyées par l'application pour, dans un premier temps, créé des réunions et contrôler les tentatives de connexions. Dans un second temps, il détermine s'il y a eu une ou plusieurs **fraude** pendant l'examen. Pour se faire, il traite :

- l'**accéléromètre** envoyé par la tête et/ou la main
- les **images** envoyées par la caméra (tête)

En parallèle, il utilise la webcam du PC pour vérifier qu'il n'y a pas d'objets ou d'autre personne dans la pièce où a lieu l'examen.

## Evironnement de travail

### Application
javac 17.0.1
Android studio

### GRPC
```python
python -m pip install --upgrade pip
python -m pip install grpcio
python -m pip install grpcio-tools
```

### Serveur
Python 3.8.1
pip 9.0.1 (ou plus)
<compléter partie soso>

## Mini démo

<Mini vidéo>
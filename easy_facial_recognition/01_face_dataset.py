''''
Capture multiple Faces from multiple users to be stored on a DataBase (dataset directory)
	==> Faces will be stored on a directory: dataset/ (if does not exist, pls create one)
	==> Each face will have a unique numeric integer ID as 1, 2, 3, etc                       

Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18    

-----------------------------------------------------------------------------------------

Ce fichier a été tiré du fichier github suivant :

https://github.com/Mjrovai/OpenCV-Face-Recognition/tree/master/FacialRecognition

Et plus précisément :

https://github.com/Mjrovai/OpenCV-Face-Recognition/blob/master/FacialRecognition/01_face_dataset.py

'''


import cv2
import os

cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video width
cam.set(4, 480) # set video height

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# For each person, enter face id
#Ici le message affiché change légèrement
# https://github.com/Mjrovai/OpenCV-Face-Recognition/blob/master/FacialRecognition/01_face_dataset.py#:~:text=face_id%20%3D%20input(%27%5Cn%20enter%20user%20id%20end%20press%20%3Creturn%3E%20%3D%3D%3E%20%20%27)
face_id = input('\n enter user name end press <return> ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

while(True):

    ret, img = cam.read()
    # img = cv2.flip(img, -1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        #Ici j'ai modifié la ligne qui était dans l'ancien fichier pour mettre le nom
        # de la personne qui passe l'examen en nom de l'image générée
        # Save the captured image into the datasets folder
        cv2.imwrite("known_faces/" + face_id + ".jpg", img[y:y+h,x:x+w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    # Je change le nombre de photos prises, 1 photo au lieu de 30
    elif count >= 1: # Take 1 face sample and stop video
         break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()



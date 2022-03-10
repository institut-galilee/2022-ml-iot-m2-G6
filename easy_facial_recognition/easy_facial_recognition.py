# Code Anis - Defend Intelligence

'''
Ce fichier vient du dossier github suivant :

https://github.com/anisayari/easy_facial_recognition

Donc les dossiers known_faces et pretrained_model proviennent également de ce lien github.

'''

import cv2
import dlib
import PIL.Image
import numpy as np
from imutils import face_utils
import argparse
from pathlib import Path
import os
import ntpath
import datetime
import glob
import time
from imutils.video import FPS

parser = argparse.ArgumentParser(description='Easy Facial Recognition App')
parser.add_argument('-i', '--input', type=str, required=True, help='directory of input known faces')

print('[INFO] Starting System...')
print('[INFO] Importing pretrained model..')
pose_predictor_68_point = dlib.shape_predictor("pretrained_model/shape_predictor_68_face_landmarks.dat")
# J'ai ajouté ce modèle pré-entrainé qui est une amélioration du predictor 68 points 
#(les points correspondent aux caractéristiques de notre visage) 
pose_predictor_68_point_gtx = dlib.shape_predictor("pretrained_model/shape_predictor_68_face_landmarks_GTX.dat")
pose_predictor_5_point = dlib.shape_predictor("pretrained_model/shape_predictor_5_face_landmarks.dat")
face_encoder = dlib.face_recognition_model_v1("pretrained_model/dlib_face_recognition_resnet_model_v1.dat")
face_detector = dlib.get_frontal_face_detector()
print('[INFO] Importing pretrained model..')

#La variable recording sert à savoir s'il on est en train d'enregistrer ou non
recording = False
# C'est le compteur qui va permettre de savoir combien de fois on a voulu enregistrer via la webcam
videono = 0
# Cette ligne va servir de nom de fichier pour l'enregistrement vidéo qui sera pris lors d'une
# suspicion de triche
# cette ligne est inspirée de ce site : https://github.com/augmentedstartups/Face-Recogntion-PyQt/blob/master/Face_Detection_PyQt_base/out_window.py#:~:text=date_time_string%20%3D%20datetime.datetime.now().strftime(%22%25y/%25m/%25d%20%25H%3A%25M%3A%25S%22)
date_string = datetime.datetime.now().strftime("%Y-%m-%d  %I.%M.%S%p   %A")
global out 

'''
Ces trois prochaines lignes viennent de ce tutoriel pour pouvoir enregistrer via la webcam 
de l'ordinateur :

https://www.codingforentrepreneurs.com/blog/how-to-record-video-in-opencv-python/#:~:text=os%0Aimport%20cv2-,filename,-%3D%20%27video.avi%27%0Aframes_per_second

Donc on donne le nom du fichier, le nombre de frames par seconde et la résolution. Cette dernière
a pour valeur 480p car l'ordinateur n'a pas pu supporter une résolution 720p
'''
# filename = 'video'+ str(videono) + '.avi'
filename = date_string + '.avi'
frames_per_second = 25   #24.0
res = '480p'

def transform(image, face_locations):
    coord_faces = []
    for face in face_locations:
        rect = face.top(), face.right(), face.bottom(), face.left()
        coord_face = max(rect[0], 0), min(rect[1], image.shape[1]), min(rect[2], image.shape[0]), max(rect[3], 0)
        coord_faces.append(coord_face)
    return coord_faces


def encode_face(image):
    face_locations = face_detector(image, 1)
    face_encodings_list = []
    landmarks_list = []
    for face_location in face_locations:
        # DETECT FACES
        shape = pose_predictor_68_point_gtx(image, face_location)
        face_encodings_list.append(np.array(face_encoder.compute_face_descriptor(image, shape, num_jitters=1)))
        # GET LANDMARKS
        shape = face_utils.shape_to_np(shape)
        landmarks_list.append(shape)
    face_locations = transform(image, face_locations)
    return face_encodings_list, face_locations, landmarks_list


def easy_face_reco(frame, known_face_encodings, known_face_names):
    rgb_small_frame = frame[:, :, ::-1]
    # ENCODING FACE
    face_encodings_list, face_locations_list, landmarks_list = encode_face(rgb_small_frame)
    face_names = []
    for face_encoding in face_encodings_list:
        if len(face_encoding) == 0:
            return np.empty((0))
        # CHECK DISTANCE BETWEEN KNOWN FACES AND FACES DETECTED
        vectors = np.linalg.norm(known_face_encodings - face_encoding, axis=1)
        tolerance = 0.5
        result = []
        for vector in vectors:
            if vector <= tolerance:
                result.append(True)
            else:
                result.append(False)
        if True in result:
            first_match_index = result.index(True)
            name = known_face_names[first_match_index]
        else:
            name = "Unknown"
        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations_list, face_names):
        # print(name)
        if name=="Unknown":
           global videono
           global recording
           recording = True
           videono += 1
        # On archive toute personne reconnue ou non avec la date dans ce fichier csv, le lien vers la source :
        # https://github.com/augmentedstartups/Face-Recogntion-PyQt/blob/master/Face_Detection_PyQt_base/out_window.py#:~:text=with%20open(%27Attendance.csv%27%2C%20%27a%27)%20as%20f%3A
        with open('Attendance.csv', 'a') as f:
                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                f.writelines(f'\n{name},{date_time_string}')
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 2, bottom - 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)

    for shape in landmarks_list:
        # S'il y a plus d'une personne ou qu'il n'y a personne, j'enregistre
        if len(landmarks_list) > 1 or len(landmarks_list) == 0 :
            # print(len(landmarks_list))
            recording = True
            videono += 1
        for (x, y) in shape:
            cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)

    return face_names


'''
Ce bloc de code appartient précédent site qui permet d'enregistrer des vidéos :

https://www.codingforentrepreneurs.com/blog/how-to-record-video-in-opencv-python/#:~:text=kirr.co/0l6qmh-,def%20change_res,-(cap%2C%20width%2C%20height
'''
#----------------------------------------------------------------------------
# Set resolution for the video capture
# Function adapted from https://kirr.co/0l6qmh
def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height

# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
      return  VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

#-----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parser.parse_args()

    # Ici on demande qu'elle est la personne qui essaye de passer l'examen
    # Le message affiché change légèrement de la source :
    # https://github.com/Mjrovai/OpenCV-Face-Recognition/blob/master/FacialRecognition/01_face_dataset.py#:~:text=face_id%20%3D%20input(%27%5Cn%20enter%20user%20id%20end%20press%20%3Creturn%3E%20%3D%3D%3E%20%20%27)
    face_id = input('\n Enter user name end press <return> ==>  ')

    print('\n[INFO] Importing faces...')
    face_to_encode_path = Path(args.input)
    files = [file_ for file_ in face_to_encode_path.rglob('*.jpg')]

    for file_ in face_to_encode_path.rglob('*.png'):
        files.append(file_)
    if len(files)==0:
        raise ValueError('No faces detect in the directory: {}'.format(face_to_encode_path))
    known_face_names = [os.path.splitext(ntpath.basename(file_))[0] for file_ in files]

    known_face_encodings = []
    for file_ in files:
        image = PIL.Image.open(file_)
        image = np.array(image)
        face_encoded = encode_face(image)[0][0]
        known_face_encodings.append(face_encoded)

    print('[INFO] Faces well imported')
    print('[INFO] Starting Webcam...')
    video_capture = cv2.VideoCapture(0)
    time.sleep(2.0)
    # Cette prochaine ligne est tirée de ce lien : https://github.com/PyImageSearch/imutils/blob/master/demos/fps_demo.py#:~:text=src%3D0).start()-,fps%20%3D%20FPS().start(),-%23%20loop%20over%20some
    # Le but est de mesurer le temps écoulé de l'examen
    fps = FPS().start()
    # Lancement de l'enregistrement :
    # https://www.codingforentrepreneurs.com/blog/how-to-record-video-in-opencv-python/
    out = cv2.VideoWriter('recording/' + filename, get_video_type(filename), frames_per_second, get_dims(video_capture, res))
    print('[INFO] Webcam well started')
    print('[INFO] Detecting...')

    #Si le répertoire Students n'est pas crée, je le crée
    if not os.path.exists('Students'):
        os.makedirs('Students')
    #Ensuite, si le dossier de la personne qui s'est identifiée n'est pas créé je le crée
    #Ces dossiers sont créés pour constituer des preuves pour la suspicions de triche
    if not os.path.exists('Students/' + face_id.upper()):
        os.makedirs('Students/' + face_id.upper())
    while True:
        ret, frame = video_capture.read()
        name = easy_face_reco(frame, known_face_encodings, known_face_names)
        # print(name)

        #Pour la ou les personne(s) qu'on aurait pu apercevoir via la webcam
        for x in name:
            # Si le nom donné ne correspond pas à l'un des noms se trouvant dans le dossier 
            # known_faces alors on enregistre
            if face_id.upper().find(x.upper()) < 0 :
                videono += 1
                recording = True
            
            nom = 'Students/' + face_id.upper() + '/'    
            file_attendance =  nom + 'Attendance_' + face_id.upper() + '.csv'
            # Ces prochaines lignes proviennent de ce lien github :
            # https://github.com/augmentedstartups/Face-Recogntion-PyQt/blob/master/Face_Detection_PyQt_base/out_window.py#:~:text=with%20open(%27Attendance.csv%27%2C%20%27a%27)%20as%20f%3A
            # On va reporter tout ce que voit la reconnaissance faciale dans un fichier csv dédié
            # Il contiendra le nom et la date, si c'est une personne inconnue il conviendra d'afficher le message : Tentative possible de triche avec la date
            with open(file_attendance, 'a') as f:
                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                f.writelines(f'\n{name[0]},{date_time_string}')
                if name[0] == 'Unknown':
                    date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                    f.writelines(f'\n{"Tentative possible de triche"},{date_time_string}')
        cv2.imshow('Easy Facial Recognition App', frame)
        if recording :
            out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if recording:
                recording = False
                out.release()
            break
        # if cv2.waitKey(1) & 0xFF == ord('e'):
        #     # global recording
        #     recording = False
        #     out.release()
       
        # update the FPS counter
        fps.update()
        
    # stop the timer and display FPS information
    # De même ces lignes viennent du même site pour mesurer le temps écoulé de l'examen :
    # https://github.com/PyImageSearch/imutils/blob/master/demos/fps_demo.py
    # J'ai changé le format du temps écoulé qui était en secondes en : hh:mm:ss 
    fps.stop()
    ty_res = time.gmtime(fps.elapsed())
    res = time.strftime("%H:%M:%S",ty_res)
    print("[INFO] Elapsed time: " + res )
    # print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed))
    # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    print('[INFO] Stopping System')
    video_capture.release()
    cv2.destroyAllWindows()
    if videono == 0 :
        out.release()
        # Je supprime le fichier vidéo s'il n'y a pas eu de suspicion de triche 
        # Les deux lignes sont inspirées de ce lien :
        # https://stackoverflow.com/questions/45458261/how-to-delete-image-video-files-in-python-3-with-jpg-mp4#:~:text=for%20i%20in%20glob.glob(%22*.png%22)%3A%0A%20%20%20%20os.remove(i)
        for i in glob.glob('recording/' + filename):
            os.remove(i)
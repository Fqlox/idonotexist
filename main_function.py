import face_recognition

#import cv2

from PIL import Image, ImageDraw, ImageOps
import numpy as np
import codecs, json 
from subprocess import run

from pathlib import Path

from io import BytesIO, StringIO
import base64


num_to_print = 5
# Couleur des landmarks
color = (0, 0, 0)

# Draw landmarks, not used Here
def visage_landmarks(visage_load, size):
    '''
    Produit une image des landmarks du visage

    :param visage_load: visage sous forme de numpy array
    :param size: tupple de la hauteur - largeur de l'image 

    :return: Image Pillows contenant les traits du visage
    '''

    # On recupère les landmarks du visage
    # TODO: passé en mode non liste !
    face_landmarks_list = face_recognition.face_landmarks(visage_load)
    face_locations = face_recognition.face_locations(visage_load)
    top, right, bottom, left = face_locations[0]
    
    # Création d'une image transparente
    width, height = size

    blank_image = np.full((width, height, 3) , (255, 255, 255), np.uint8)
    pil_image = Image.fromarray(blank_image)
    d = ImageDraw.Draw(pil_image, 'RGB')


    for face_landmarks in face_landmarks_list:
        for facial_feature in face_landmarks:
            # Ajout d'effet de maquillage ??? (cad différentiation des structures faciales)
            d.line(face_landmarks[facial_feature], width=3, fill=color)
    
    #face_image = pil_image[top:bottom, left:right]
    margin = 20
    face_image = pil_image.crop((left - margin, top - margin, right + margin, bottom + margin))

    return face_image



def compare_visage_to_dataset(visage_encoding, path_to_dir):
    '''
    Renvoie les visages issues de la base de donnée les plus proches du visage montré

    :param visage_encoding: numpy array de 128 dimension de 
    :param path_to_dir: chemin vers les deux base de données de visage 
                            - stylegan05 pour le stylegan avec en psi 0.5
                            - stylegan10 pour le stylegan avec en psi 1.0
                        Ces deux base represente un peu moins de 200k données de visages

    :return: tupple comprenant les 5 visages les plus proches du resultat 

    '''
    # chargement des data des visages 

    # TODO: PATHLIB HERE
    all_data = np.load(Path(path_to_dir, "faces_data.npy"))
    # chargement des listes des chemins vers les photos de visage
    with open(Path(path_to_dir, "face_list_all.json")) as f:
        all_file_name = json.load(f)


    distances = face_recognition.face_distance(all_data, visage_encoding)

    # listes des valeurs de distance couplé avec les chemins des fichiers 
    # [(0.877, "img1.jpg") , (0.02, "img2.jpg")]  
    tuples_file_distance = [(dist , all_file_name[index]) for index, dist in enumerate(distances)]

    #print(tupples_file_distance)

    # trie la liste des tuple suivant leurs distances 
    tuples_file_distance.sort(key=lambda tup: tup[0])

    # on enregistre les tupples les plus pertients 
    tuples_distances_saved = tuples_file_distance[:num_to_print]
    # on ajoute "path_to_file" au debut du chemin d'accès
    tuples_distances_saved = [(a[0], path_to_dir + a[1]) for a in tuples_distances_saved]


    # on libère de la place dans la ram
    del all_file_name
    del all_data

    del distances
    del tuples_file_distance
    '''
    # Affichage pour le DEBUG

    for tuple_el in tuples_distances_saved:
        print(tuple_el)
        distance, file_path = tuple_el

        im = Image.open(path_to_dir + file_path)
        im.show()
    '''
    return tuples_distances_saved
 



def main(visage_load_np, visage_size):
    
    '''
    # Recuperation de l'image depuis un chemin (plus utile lorsque l'on utilise la webcam
    visage_load = Image.open(path_to_img)
    #visage_load = face_recognition.load_image_file(path_to_img)

    visage_size = visage_load.size

    visage_load_np = np.array(visage_load)
    '''
    
    
    # Création des landmarks du visage
    #visage_pillows_landmarks = visage_landmarks(visage_load_np, visage_size)
    #visage_pillows_landmarks.show()
    

    # envoie en base64
    #visage_pillows_landmarks.save('tmp/landmarks.png')
    
    visage_encoding = face_recognition.face_encodings(visage_load_np)
    if( not visage_encoding): return 

    visage_encoding = visage_encoding[0] # premier visage trouvé par l'algorithme

    # PATH LIB REQUIT
    stylegan_05 = compare_visage_to_dataset(visage_encoding, "data/stylegan05/")
    stylegan_10 = compare_visage_to_dataset(visage_encoding, "data/stylegan10/")

    tous_les_visages = stylegan_05 + stylegan_10
    tous_les_visages.sort(key=lambda tup: tup[0])

    tous_les_visages = tous_les_visages[:num_to_print] 

    faces = []

    for visage in tous_les_visages:
        
        distance, chemin = visage

        im = Image.open(chemin)

        ret = BytesIO()
        im.save(ret, im.format)
        ret.seek(0)
        im_64 = base64.b64encode(ret.getvalue()).decode("utf-8")

        faces.append({"distance": distance, "image": im_64})
    
    return faces
        




def base64Input(base64Input):

    # Conversion de base64 a Pillow
    image = Image.open(BytesIO(base64.b64decode(base64Input))).convert('RGB')

    #TODO: Ici besoin d'un système pour resize les images si elles sont trop grande

    # Conversion en numpy array
    image_np = np.array(image)
    


    # We try to see if the image contains a face before we go further
    #peut etre un resize ici pour que l'operation de detection soit plus rapide
    
    face_location = face_recognition.face_locations(image_np)


    if(not face_location): return ({"error" : "No face"})

    faces = main(image_np, (image_np.shape[0], image_np.shape[1]))

    if(not faces) : return ({"error" : "No face"})

    return ({
        "faces": faces
    })

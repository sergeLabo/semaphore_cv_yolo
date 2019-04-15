#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# This file is part of semaphore_cv_yolo.
#
# semaphore_cv_yolo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# semaphore_cv_yolo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################

"""
Création d'images toujours carrées avec un semaphore collé
fond = video = /video/Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg
27 lettres
Fichier txt avec
<object-class> <x> <y> <width> <height>
"""


import math
import random
import numpy as np
import cv2

from pymultilame import MyTools

L = "a bcdefghijklmnopqrstuvwxyz"
# ["a", " ", ....]
LETTRES = list(L)


class CreateShot:

    def __init__(self, size, video, number=1000):
        """
        letters = {'a': image de a,
                   ' ': image de ' ',
                   etc ...}
        """
        self.size = size
        self.number = number
        
        self.tools = MyTools()
        self.create_directories()
        self.letters = self.get_letters_images()
        self.numero_lettre = 0
        
        self.capture = cv2.VideoCapture(video)
        self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Taille Video:", self.width, self.height)

        self.get_shots()

    def create_directories(self):
        """Un dossier root=shot, un sous dossier par lettre"""
        
        self.tools.create_directory('./shot')
        for l in LETTRES:
            if l == " ":
                l = "space"
            self.tools.create_directory('./shot/shot_' + l)

    def get_letters_files(self):
        letters_files = self.tools.get_all_files_list("lettre_epaisse_alpha", ".png")
        print("Nombre de letters =", len(letters_files))
        return letters_files

    def get_letters_images(self):
        """Récupère toutes les images de lettres"""

        letters = {}
        for l_file in self.get_letters_files():
            # lettre/shot_10_j.png
            l = l_file[:-4][-1]
            img = cv2.imread(l_file, -1)
            img = delete_gray(img)
            letters[l] = img
        return letters

    def frame_resize(self, frame):
        """Pour 1024: resize puis coupe des 2 cotés de 398
        pour 416: 1280x720 devient 739x416
        """

        # Largeur
        a = int(self.width*self.size/self.height)
        # Hauteur
        b = self.size
        # Resize
        frame = cv2.resize(frame, (a, b), interpolation=cv2.INTER_AREA)

        # Coupe
        x = int((a - b)/2)
        y = 0
        w, h = self.size, self.size
        frame = frame[y:y+h, x:x+w]

        return frame

    def aspect_change(self, lettre):
        """Couleur, flou, rotation
        lettre est l'image de la lettre
        """

        bg_color = lettre[0][0]
        R = random.randint(0, 100)
        G = random.randint(0, 50)
        B = random.randint(100, 255)
        lettre[np.all(lettre == [0, 0, 0, 255], axis=2)] = [R, G, B, 255]
        mask = np.all(lettre == bg_color, axis=2)
        lettre[mask] = [0, 0, 0, 0]

        # Rotation
        some = random.randint(-3, 3)
        lettre = rotateImage(lettre, some)

        # Flou de 0 à 4
        flou = random.randint(0, 4)
        if flou != 0:
            lettre = cv2.blur(lettre, (flou, flou))
            
        return lettre
        
    def lettre_image_change(self, lettre):
        """Adapte une lettre, calcule taille, position, flou, couleur
        lettre est l'image de la lettre
        """

        # Modification de l'aspect
        lettre = self.aspect_change(lettre)
        
        # Variation sur la taille du sémaphore
        semaphore_mini = int(self.size/7)

        w, h = lettre.shape[1], lettre.shape[0]
        # Set de la hauteur, puis largeur
        y_size = random.randint(semaphore_mini, int(self.size*0.8))
        x_size = int(w * y_size / h)

        # Maxi de taille de lettre < self.size
        y_size = min(y_size, self.size)
        x_size = min(x_size, self.size)
        
        lettre = cv2.resize(lettre,
                            (x_size, y_size),
                            interpolation=cv2.INTER_CUBIC)
        
        # Position posible
        x = random.randint(0, self.size - x_size)
        y = random.randint(0, self.size - y_size)
        
        return lettre, x_size, y_size, x, y
        
    def overlay(self, frame):
        """Trouve une lettre, supperpose à la frame"""

        # Lecture des lettres de l'alphabet en boucle
        l = LETTRES[self.numero_lettre]
        self.numero_lettre += 1
        if self.numero_lettre == 27:
            self.numero_lettre = 0
            
        # lettre est l'image de lettre
        lettre = self.letters[l]

        # Adaptation
        lettre, x_size, y_size, x, y = self.lettre_image_change(lettre)
        
        # Overlay
        img = over_transparent(frame, lettre, x, y)
        
        return img, l, x_size, y_size, x, y

    def save(self, img, lettre, x_size, y_size, x, y, n):
        """Enregistrement dans le dossier ./shot/shot_a/ de
        shot_0_a.jpg et shot_0_a.txt
        class position(x y) taille(x y)
        x, y position du coin haut gauche
        s = taille de la lettre
        """

        # Get indice avant modif liste
        indice = LETTRES.index(lettre)

        # pour avoir dossier clair
        if lettre == ' ':
            lettre = 'space'

        # Avec sous dossiers
        fichier = './shot/shot_' + lettre + '/shot_' + str(n) + '_' + lettre
        
        # Enregistrement de l'image
        cv2.imwrite(fichier + '.jpg', img)

        # Enregistrement des datas
        # Taille relative de l'image lettre
        tx = x_size/self.size
        ty = y_size/self.size
        
        # Origine = top left
        xc = (x + (x_size/2))/self.size
        yc = (y + (y_size/2))/self.size
        # class-position du centre-taille
        data =  str(indice) + ' '\
                + str(xc) + ' '\
                + str(yc) + ' '\
                + str(tx) + ' '\
                + str(ty)
                
        self.tools.write_data_in_file(data, fichier + '.txt', 'w')
        
    def get_shots(self):
        n, m = 0, 0
        self.loop = 1
        while self.loop:
            ret, frame = self.capture.read()
            if ret:
                # pour enregistrer 1 frame sur 10 et varier les fonds
                if n % 10 == 0:
                    frame = self.frame_resize(frame)
                    
                    # Overlay d'une lettre
                    img, l, x_size, y_size, x, y = self.overlay(frame)

                    print("Shot numéro", m, "Lettre", l)
                            
                    # Enregistrement de l'image et du fichier txt
                    self.save(img, l, x_size, y_size, x, y, m)
                    m += 1
                    
                cv2.imshow('image', img)

                # Jusqu'à number
                n += 1
                if m == self.number:
                    self.loop = 0
                
                # Echap et attente
                k = cv2.waitKey(10)
                if k == 27:
                    self.loop = 0
            else:
                # Reset si la video est terminée
                self.capture = cv2.VideoCapture(video)
                
        print("Nombre d'images crées:", m)
        cv2.destroyAllWindows()


def delete_gray(lettre):
    """Supprime le gris alpha autour des lettres
    Méthode bourrin
    """
    transp = [255, 255, 255, 0]
    for x in range(lettre.shape[1]):
        for y in range(lettre.shape[0]):
            if lettre[y, x][3] < 255:    
                lettre[y, x] = transp
        
    return lettre
    
def rotateImage(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1],
                            flags=cv2.INTER_LINEAR)
    return result

def over_transparent(bg, over, x, y):
    """Overlay over sur bg, à la position x, y
    x, y = coin supérieur gauche de over
    """
    
    bg_width = bg.shape[1]
    bg_height = bg.shape[0]

    if x >= bg_width or y >= bg_height:
        return bg

    h, w = over.shape[0], over.shape[1]

    if x + w > bg_width:
        w = bg_width - x
        over = over[:, :w]

    if y + h > bg_height:
        h = bg_height - y
        over = over[:h]

    if over.shape[2] < 4:
        over = np.concatenate([over,
                               np.ones((over.shape[0],
                                        over.shape[1],
                                        1),
                               dtype=over.dtype) * 255],
                               axis = 2,)

    over_image = over[..., :3]
    mask = over[..., 3:] / 255.0
    bg[y:y+h, x:x+w] = (1.0 - mask) * bg[y:y+h, x:x+w] + mask * over_image

    return bg


if __name__ == "__main__":
    video = 'video/Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg'
    # Taille des images multiple de 32, 32*20=640
    # 2000 images par classe 2000x27=54000 + 6000 de test
    cs = CreateShot(640, video, number=60000)

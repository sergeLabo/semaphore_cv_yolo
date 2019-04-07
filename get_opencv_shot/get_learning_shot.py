#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# This file is part of Mon Semaphore.
#
# Mon Semaphore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mon Semaphore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################

"""
Création d'images toujours carrées avec un semaphore collé

fond = video = /video/Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg
27 lettres
image de 1024x1024
<object-class> <x> <y> <width> <height>
"""


import math
import random
import numpy as np
import cv2
from PIL import Image

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
        self.tools.create_directory('./shot_test')

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
        """Couleur, flou, rotation"""

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
        #img = over_transparent(frame, lettre, x, y)
        img = pil_overlay(frame, lettre)
        
        return img, l, x_size, y_size, x, y

    def save(self, img, lettre, x_size, y_size, x, y, n):
        """Enregistrement dans le dossier ./shot/lettre/ de
        toto.png
        et
        toto.txt
        class position(x y) taille(x y)
        x, y position du coin haut gauche
        s = taille de la lettre
        """

        # Get indice avant modif liste
        indice = LETTRES.index(lettre)

        # pour avoir dossier clair
        if lettre == ' ':
            lettre = 'space'

        # Sans sous dossiers
        fichier = './shot_test/shot_' + str(n) + '_' + lettre
        
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
            # #b_channel, g_channel, r_channel = cv2.split(frame)
            # ## Creating a dummy alpha channel image
            # #alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 50 
            # #frame = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
            
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

def pil_overlay(im1, im2):

    return Image.alpha_composite(im1, im2)

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
    
def rotate_image(image, angle):
    '''Rotate image "angle" degrees.

    How it works:
    - Creates a blank image that fits any rotation of the image. To achieve
      this, set the height and width to be the image's diagonal.
    - Copy the original image to the center of this blank image
    - Rotate using warpAffine, using the newly created image's center
      (the enlarged blank image center)
    - Translate the four corners of the source image in the enlarged image
      using homogenous multiplication of the rotation matrix.
    - Crop the image according to these transformed corners
    '''

    diagonal = int(math.ceil(math.sqrt(pow(image.shape[0], 2) + pow(image.shape[1], 2))))
    offset_x = (diagonal - image.shape[0])/2
    offset_y = (diagonal - image.shape[1])/2
    dst_image = np.zeros((diagonal, diagonal, 3), dtype='uint8')
    image_center = (float(diagonal-1)/2, float(diagonal-1)/2)

    R = cv2.getRotationMatrix2D(image_center, -angle, 1.0)
    dst_image[offset_x:(offset_x + image.shape[0]), offset_y:(offset_y + image.shape[1]), :] = image
    dst_image = cv2.warpAffine(dst_image, R, (diagonal, diagonal), flags=cv2.INTER_LINEAR)

    # Calculate the rotated bounding rect
    x0 = offset_x
    x1 = offset_x + image.shape[0]
    x2 = offset_x + image.shape[0]
    x3 = offset_x

    y0 = offset_y
    y1 = offset_y
    y2 = offset_y + image.shape[1]
    y3 = offset_y + image.shape[1]

    corners = np.zeros((3,4))
    corners[0,0] = x0
    corners[0,1] = x1
    corners[0,2] = x2
    corners[0,3] = x3
    corners[1,0] = y0
    corners[1,1] = y1
    corners[1,2] = y2
    corners[1,3] = y3
    corners[2:] = 1

    c = np.dot(R, corners)

    x = int(round(c[0,0]))
    y = int(round(c[1,0]))
    left = x
    right = x
    up = y
    down = y

    for i in range(4):
        x = c[0,i]
        y = c[1,i]
        if (x < left): left = x
        if (x > right): right = x
        if (y < up): up = y
        if (y > down): down = y
    h = int(round(down - up))
    w = int(round(right - left))
    left = int(round(left))
    up = int(round(up))

    cropped = np.zeros((w, h, 3), dtype='uint8')
    cropped[:, :, :] = dst_image[left:(left+w), up:(up+h), :]
    return cropped

def rotateImage(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1],
                            flags=cv2.INTER_LINEAR)
    return result

def deform_rotation(lettre, angle):
    # Rotation qui déforme l'image
    rows, cols, a = lettre.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2), angle, 1)
    lettre = cv2.warpAffine(lettre, M, (cols, rows))
    return lettre

def transparent_overlay(src , overlay , pos=(0,0), scale = 1):
    """Overlay a transparent image on backround.
    :param src: Input Color Background Image
    :param overlay: transparent Image (BGRA)
    :param pos:  position where the image to be blit.
    :param scale : scale factor of transparent image.
    :return: Resultant Image
    """

    overlay = cv2.resize(overlay, (0, 0), fx=scale, fy=scale)
    
    # Size of pngImg
    h,w,_ = overlay.shape
      
    # Size of background Image
    rows,cols,_ = src.shape
    
    # Position of PngImage 
    y, x = pos[0],pos[1]    
    
    # Loop over all pixels and apply the blending equation
    for i in range(h):
        for j in range(w):
            if x+i >= rows or y+j >= cols:
                continue
            alpha = float(overlay[i][j][3]/255.0) # read the alpha channel 
            src[x+i][y+j] = alpha*overlay[i][j][:3]+(1-alpha)*src[x+i][y+j]
    return src


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
    cs = CreateShot(640, video, 5)

"""
    x_offset = y_offset = 50
    y1, y2 = y_offset, y_offset + over.shape[0]
    x1, x2 = x_offset, x_offset + over.shape[1]

    alpha_s = over[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        bg[y1:y2, x1:x2, c] = (alpha_s * over[:, :, c] +
                                  alpha_l * bg[y1:y2, x1:x2, c])
    return bg
"""

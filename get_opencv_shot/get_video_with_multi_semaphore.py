#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import random
import numpy as np
import cv2
from pymultilame import MyTools


class GetVideoWithSemaphore:

    def __init__(self, video_in, video_out, lenght, every):
        """  """
        self.video_in = video_in
        self.video_out = video_out
        self.lenght = lenght
        self.every = every * 24
        # [[y_size, x_pos, y_pos]]
        self.size_pos_list = []
            
        # mes outils perso: pymultilame
        self.tools = MyTools()

        self.letters = self.get_letters_images()
        self.numero_lettre = 0

        # Video d'entrèe
        self.video_in = cv2.VideoCapture(video_in)
        self.width = int(self.video_in.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video_in.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.FPS = self.video_in.get(cv2.CAP_PROP_FPS)
        print("Video d'entrèe:", self.width, self.height, self.FPS)

        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        self.video = cv2.VideoWriter(self.video_out,fourcc, float(self.FPS),
                                    (self.width, self.height))

        # Lance la création de la video
        self.get_semaphore_video()

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
            letters[l] = cv2.imread(l_file, -1)
        return letters
        
    def overlay(self, frame, lettre_img_list, lettre_list, change):
        """ Conservation dans self.size_pos_list = [[y_size, x_pos, y_pos]]
        lettre_img_list: liste des images des lettres [image_de_a, image_de_f, ...]
        lettre_list: liste des lettres ['a', 'f', ...]
        change = changement de lettre, soit affichage des lettres en cours
        """

        for i in range(len(lettre_list)):
            # changement seulement à every
            if change == 1:
                # Plage de taille possible
                h_mini_semaphore = int(self.height/10)
                h_maxi_semaphore = int(self.height/1.2)
                # Choix
                y_size = random.randint(h_mini_semaphore, h_maxi_semaphore)
                # x découle de y
                x_size = int(lettre_img_list[i].shape[1] * \
                             y_size/lettre_img_list[i].shape[0])
                # Application de la taille à la lettre en cours
                img = cv2.resize(lettre_img_list[i], (x_size, y_size),
                                 interpolation=cv2.INTER_CUBIC)
                # Position
                x_pos = random.randint(50, self.width - x_size - 50)
                y_pos = random.randint(0, self.height - y_size)           

                # Storage
                self.size_pos_list.append([y_size, x_pos, y_pos])
                print("Ajout de", [y_size, x_pos, y_pos])
            else:  # change == 0
                y_size = self.size_pos_list[i][0]
                x_size = int(lettre_img_list[i].shape[1] * \
                             y_size/lettre_img_list[i].shape[0])
                x_pos = self.size_pos_list[i][1]
                y_pos = self.size_pos_list[i][2]
                img = cv2.resize(lettre_img_list[i], (x_size, y_size),
                                 interpolation=cv2.INTER_CUBIC)

            # Modification de l'aspect de la lettre
            img = aspect_change(img)
            # Overlay de lettre_img déjà retaillée à position x, y
            frame = over_transparent(frame, img, x_pos, y_pos)
            
        return frame

    def add_lettre(self, frame, lettre_list):
        k = 0
        for l in lettre_list:
            if l == " ":
                l = "space"
            # Overlay du caractère l
            font = cv2.FONT_HERSHEY_SIMPLEX
            frame = cv2.putText(frame, l, (10, int(self.height*(0.95-k))),
                                font, 1, (255,255,255),
                                2, cv2.LINE_AA)
            k += 0.06
        return frame
            
    def get_lettre_list(self):
        """Retourne une liste d'image de lettres et une liste de ces lettres"""

        # Get some lettres au hasard
        lettre_list = []
        lettre_img_list = []
        
        # Get n lettres
        n = random.randint(1, 3)
        for i in range(n):
            k = random.randint(0, 26)
            lettre_list.append(list(self.letters.keys())[k])
            
        print("\nListe des lettre:", lettre_list, "\n")

        for u in range(len(lettre_list)):
            lettre_img_list.append(self.letters[lettre_list[u]])
            
        return lettre_img_list, lettre_list
        
    def get_semaphore_video(self):
        """Une lettre ajoutée et changée toutes les every secondes"""
        
        how_many = 0
        letter_duration = 0
        loop = 1
        change = 1
        
        # Initialisation
        lettre_img_list, lettre_list = self.get_lettre_list()
        
        while loop:
            ret, frame = self.video_in.read()
            
            letter_duration += 1
            # Changement de lettres
            if letter_duration == self.every:
                lettre_img_list, lettre_list = self.get_lettre_list()
                change = 1
                # Reset
                self.size_pos_list = []
                letter_duration = 0
                
            # Overlay des images de lettres
            frame = self.overlay(   frame,
                                    lettre_img_list,
                                    lettre_list,
                                    change)
            # Overlay des textes de lettres                        
            frame = self.add_lettre(frame, lettre_list)
            # On reste sur les mêmes lettres pendant every
            change = 0
                    
            cv2.imshow('Out', frame)
            self.video.write(frame)

            # Jusqu'à la durée demandée
            how_many += 1
            if how_many == self.FPS * self.lenght:
                loop = 0
            # Echap et attente
            k = cv2.waitKey(33)
            if k == 27:
                loop = 0
                
        self.video.release()
        cv2.destroyAllWindows()


def aspect_change(lettre):
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
    video_in = 'video/Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg'
    video_out = 'video/cv_axe.avi'
    lenght = 180  # secondes
    every = 2  # une lettre changée toutes les 1 seconde
    gvws = GetVideoWithSemaphore(video_in, video_out, lenght, every)

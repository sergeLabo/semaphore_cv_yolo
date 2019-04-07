#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import random
import numpy as np
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from pymultilame import MyTools


class GetVideoWithSemaphore:

    def __init__(self, video_in, video_out, lenght, every):
        """  """
        self.video_in = video_in
        self.video_out = video_out
        self.lenght = lenght
        self.every = every * 24
        self.y_fix = 0
        self.x_pos = 0
        self.y_pos = 0
            
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
        letters_files = self.tools.get_all_files_list("lettre", ".png")
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
        
    def overlay(self, frame, lettre_img, lettre, change):
        """
        lettre 320x320 variation 100 à 800
        frame 1024x1024
        position
            exempe 624: 1024-624 = 400 
        """
        
        # Variation sur la taille du sémaphore
        semaphore_mini = int(self.height/7)

        w, h = lettre_img.shape[1], lettre_img.shape[0]
        
        # Set de la hauteur, puis largeur
        if change == 1:  # changement seulement à every
            y_size = random.randint(semaphore_mini, int(self.height*0.8))
            self.y_fix = y_size
        else:
            y_size = self.y_fix
            
        x_size = int(w * y_size / h)

        # Maxi de taille de lettre_img < self.height
        y_size = min(y_size, self.height)
        x_size = min(x_size, self.height)
        
        lettre_img = cv2.resize(lettre_img,
                            (x_size, y_size),
                            interpolation=cv2.INTER_CUBIC)
        
        # Position posible
        if change == 1:  # changement seulement à every
            x = random.randint(0, self.height - x_size)
            self.x_pos = x
            y = random.randint(0, self.height - y_size)
            self.y_pos = y
        else:
            x = self.x_pos
            y = self.y_pos
            
        img = over_transparent(frame, lettre_img, x, y)

        # Overlay du caractère l
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, lettre, (10, int(self.height*0.8)),
                    font, 4, (255,255,255),
                    2, cv2.LINE_AA)
    
        return img

    def get_lettre(self):
        # Lecture des lettres de l'alphabet en boucle
        l = list(self.letters.keys())[self.numero_lettre]
        print("Lettre en cours", l, self.numero_lettre)
        self.numero_lettre += 1
        if self.numero_lettre == 27:
            self.numero_lettre = 0
        lettre_img = self.letters[l]
        return lettre_img, l
        
    def get_semaphore_video(self):
        """Une lettre ajoutée et changée toutes les every secondes"""
        
        how_many = 0
        letter_duration = 0
        loop = 1
        change = 1
        
        # Initialisation
        lettre_img, lettre = self.get_lettre()
        
        while loop:
            ret, frame = self.video_in.read()
            letter_duration += 1
            if letter_duration == self.every:
                # lettre_img est l'image de la lettre lettre
                lettre_img, lettre = self.get_lettre()
                change = 1
                letter_duration = 0
                
            # Overlay d'une lettre
            frame = self.overlay(frame, lettre_img, lettre, change)
            change = 0
                    
            cv2.imshow('Out', frame)
            self.video.write(frame)

            # Jusqu'à la durée demandée
            how_many += 1
            if how_many == self.FPS * self.lenght:
                loop = 0
            # Echap et attente
            k = cv2.waitKey(2)
            if k == 27:
                loop = 0
                
        self.video.release()
        cv2.destroyAllWindows()


def over_transparent(bg, over, x, y):
    """Overlay over sur bg, à la position x, y
    x, y = coin supérieur gauche de overlay
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
    video_out = 'video/semaphore.avi'
    lenght = 180  # secondes
    every = 2  # une lettre changée toutes les 1 secondes
    gvws = GetVideoWithSemaphore(video_in, video_out, lenght, every)

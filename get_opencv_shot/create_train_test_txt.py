#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import random
from pymultilame import MyTools

mt = MyTools()

# Dossier des images et txt
shot_dir = '/media/data/3D/projets/semaphore_cv_yolo/get_opencv_shot/shot/'

# liste de toutes les images
files = mt.get_all_files_list(shot_dir, '.jpg')
# Rebat les cartes pour prendre les fichiers au hazard dans les sous-dossiers
random.shuffle(files)
print("Nombre de fichiers", len(files))

train_num = 54000
test_num = 6000

counter = 0
train = ""
test = ""

a,b,c,d,e = 0,0,0,0,0

for f in files:  
    if counter < train_num:
        train += f + "\n"
        if "_a.jpg" in f:
            a += 1
        if "_b.jpg" in f:
            b += 1
        if "_a.jpg" in f:
            c += 1
        if "_a.jpg" in f:
            d += 1
        if "_a.jpg" in f:
            e += 1
    else:
        test += f + "\n"
    counter += 1

print("Nombre de a,b,c,d,e : ", a,b,c,d,e)

# Ecriture dans les fichiers
mt.write_data_in_file(test, "test.txt", "w")
mt.write_data_in_file(train, "train.txt", "w")

print("Done.")

#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


from pymultilame import MyTools

mt = MyTools()

# Dossier des images et txt
current_dir = '/media/data/3D/projets/semaphore_v4/get_opencv_shot'

# liste de toutes les images
files = mt.get_all_files_list(current_dir, '.jpg')

train_num = 54000
test_num = 6000
print("Nombre de fichiers train", train_num)
print("Nombre de fichiers test", test_num)

counter = 0
train = ""
test = ""

for f in files:  
    if counter < train_num:
        train += f + "\n"
    else:
        test += f + "\n"
    counter += 1
    
# Ecriture dans les fichiers
mt.write_data_in_file(test, "test.txt", "w")
mt.write_data_in_file(train, "train.txt", "w")

print("Done.")

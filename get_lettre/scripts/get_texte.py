#! /usr/bin/env python2
# -*- coding: utf-8 -*-

from pymultilame import MyTools


def get_text_str_from_this_script():
    mt = MyTools()
    
    text_file_list = mt.get_all_files_list('./texte', '.txt')
    print('Liste des fichiers texte =', text_file_list)

    text_str = get_str(text_file_list)
    return text_str
    
def get_text_str_from_blender(dossier):
    mt = MyTools()
    
    text_file_list = mt.get_all_files_list(dossier, '.txt')
    print('Liste des fichiers texte =', text_file_list)

    text_str = get_str(text_file_list)
    return text_str
    
def get_str(text_file_list):
    mt = MyTools()
    text_str = ''
    for f in text_file_list:
        text = mt.read_file(f)
        text_str += text

    text_str = get_ascii(text_str)
    return text_str

def get_ascii(text_str):
    text_ascii = ''
    non_utilisable = 0
    for lettre in text_str:
        if lettre.isalpha() or lettre == ' ':
            text_ascii += lettre
        else:
            non_utilisable += 1
    print('Nombre de caractères non utilisables =', non_utilisable)
    return text_ascii

def read_texte(text_str):
    for lettre in text_str:
        print(lettre)
    
if __name__ == '__main__':
    text_str = get_text_str_from_this_script()
    print(text_str)
    read_texte(text_str)

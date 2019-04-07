#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# This file is part of Semaphore.
#
# Semaphore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Semaphore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################


"""
Lancé à chaque frame durant tout le jeu.
"""

import os
from time import sleep
import math
from random import uniform

from bge import logic as gl
from bge import render


def main():
    if gl.tempoDict['frame'].tempo % 60 == 0:
        print("Shot n°", gl.numero)

    # Les différentes phases du jeu
    if gl.tempoDict['shot'].tempo == gl.chars_change:
        gl.chars = get_chars()
        display(gl.chars)
        # glissement rotation à chaque nouveau caractère du socle
        if not gl.static:
            #glissement_socle()
            #change_socle_position()
            glissement_socle()
            rotation_socle()

    if gl.tempoDict['shot'].tempo == gl.make_shot:
        make_shot()

    # Fin du jeu à nombre_shot_total
    end()

    # Toujours partout, tempo 'shot' commence à 0
    gl.tempoDict.update()

def glissement_socle():
    """ y = random -2 à 4
    si y = -2:
                x = 0
                z = -3.2
    si y = 1:
                x = -1.3 à 1.3
                z =   -1.7 à 1.9
    si y = 4 :
                x = -2.5 à 2.5
                z = -3.2 à 2.8
    2.5/6 = 0.416

    pour 1er grand test: 90.6 %
    # Perspective
    gl.y = uniform(-2, 4)
    gl.x = 0.5 * uniform(-(0.8 + gl.y*0.416), 0.8 + gl.y*0.416)
    gl.z = 0.5 * uniform(-3.2 , gl.y - 1.2) - 1

    pour 2ème test:  93.15% allongé 20%
    # Perspective angle 8°caméra focal 35
    gl.y = uniform(-2, 4)
    gl.x = 0.8 * uniform(-(1.8 + gl.y*0.416), 0.7 + gl.y*0.416)
    gl.z = 0.5 * uniform(-4 , gl.y - 1.2) - 1.3

    pour 3ème test: angle 8° mât aggrandi, bras central allongé
    # Perspective angle 8°caméra focal 30
    gl.y = uniform(-2, 4)
    gl.x = 1.0 * uniform(-(1.8 + gl.y*0.416), 0.7 + gl.y*0.416)
    gl.z = 0.8 * uniform(-4 , gl.y - 0.2) - 3
    """

    # Perspective
    gl.y = uniform(-2, 4)
    gl.x = 1.0 * uniform(-(1.8 + gl.y*0.416), 0.7 + gl.y*0.416)
    gl.z = 0.8 * uniform(-4 , gl.y - 0.2) - 3

    # J'applique
    gl.socle.worldPosition[0] = gl.x
    gl.socle.worldPosition[1] = gl.y
    gl.socle.worldPosition[2] = gl.z

def rotation_socle():
    angle = uniform(-gl.rotation_socle, gl.rotation_socle)
    xyz = gl.socle.localOrientation.to_euler()
    xyz[1] = math.radians(angle)
    gl.socle.worldOrientation = xyz.to_matrix()

def end():
    if gl.numero == gl.nombre_shot_total:
        gl.endGame()

def display(chars):
    """Affichage de la lettre par rotation des bras."""

    # 180, 90, 0
    angles = get_angles(chars)

    xyz = gl.bras_central.worldOrientation.to_euler()
    xyz[1] = math.radians(angles[0])
    gl.bras_central.localOrientation = xyz.to_matrix()

    xyz = gl.bras_gauche.localOrientation.to_euler()
    xyz[1] = math.radians(angles[1])
    gl.bras_gauche.localOrientation = xyz.to_matrix()

    xyz = gl.bras_droit.localOrientation.to_euler()
    xyz[1] = math.radians(angles[2])
    gl.bras_droit.localOrientation = xyz.to_matrix()

def get_angles(chars):
    try:
        angles = gl.lettre_table[chars]
    except:
        angles = (0, 0, 0)
    return angles

def get_chars():
    try:
        chars = gl.text_str[gl.lettre]
        chars = chars.lower()
    except:
        gl.lettre = 0
        chars = gl.text_str[gl.lettre]
        chars = chars.lower()

    gl.lettre += 1
    return chars

def make_shot():

    name_file_shot = get_name_file_shot()
    render.makeScreenshot(name_file_shot)

    #print(gl.chars, '--> shot ' + str(gl.numero))
    gl.numero += 1

def get_name_file_shot():
    """/media/data/3D/projets/semaphore/game/shot/shot_0/shot_a_0.png
    60000
    4000
    je suis à gl.numero = 5555
    numero du dossier = n = 1 = int(5555/4000)
    """

    n = int(gl.numero / gl.nombre_de_fichiers_par_dossier)

    gl.name_file_shot = os.path.join(gl.shot_directory,
                                     'shot_' + str(n).zfill(3),
                                     'shot_' + str(gl.numero) + '_' + gl.chars + '.png')

    return gl.name_file_shot

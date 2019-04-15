# semaphore_cv_yolo

Création d'image pour tester une Intelligence Artificielle avec Yolo Darknet

### Contexte

Réalisé avec:

* Debian 10 Buster
* OpenCV 3.4
* python 3.7

### La documentation sur ressources.labomedia.org

* [Toutes les pages sur Sémaphore](https://ressources.labomedia.org/tag/semaphore?do=showtag&tag=semaphore)
* [Les pages sur Yolo Darknet](https://ressources.labomedia.org/tag/yolo_darknet?do=showtag&tag=yolo_darknet)


#### Installation
* [Mon module python perso pymultilame](https://ressources.labomedia.org/pymultilame)

  sudo pip3 install -e git+https://github.com/sergeLabo/pymultilame.git#egg=pymultilame

#### Utilisation

##### Création des images du sémaphore seul. Dans le dossier get_lettre

~~~text
blenderplayer get_lettre_epaisse.blend
~~~

Retravailler les images dans Gimp
* transparence
* resize

##### Création des images avec opencv

* mettre une video dans le dossier video
* dans get_learning_shot.py, adapter la ligne
~~~text
video = 'video/Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg'
puis
python3 get_learning_shot.py
~~~

### Remarques

La video et les images créées ne sont pas sur ce dépôt

### Merci à:

* [La Labomedia](https://ressources.labomedia.org)

# Etude longitudinale de l’évolution d’une tumeur
Ce projet a pour objectif de réaliser le suivi des changements d'une tumeur à partir de deux scans effectués sur un même patient à des dates différentes.

## Execution du code
 1. Clonez le dépôt et placez-vous dans la racine du projet.

 2. Installez les dépendances nécessaires :
```sh
pip install -r requirement.txt
```

 3. Exécutez le script principal :
```sh
python main.py
```

## Répartition du travail
Antoine HAVARD : ...

Emma CASAGRANDE : ...

Salomé BERGER : ...

Corentin COLMEL : ...

## Recalage d'images
**A compléter**, utiliser la lib itk
 - Méthode utilisée
 - Pourquoi cette méthodes
 - Les Difficultés rencontrées
 - Le résultat

### Test n°1: VersorRigid3DTransform

Pour commencer, on a voulu tester de faire un recalage en appliquant une translation et une rotation. Pour cela on a utilisé VersorRigid3DTransform
qui fonctionnait bien avec des images médicales en 3D.

**Description:** VersorRigid3DTransform applique une rotation et une translation à l'espace.

**Analyse:**

- __Image Gauche__: Fixed Image
- __Image Milieu__: Moving Image
- __Image Droite__: Résultat

<video src="images/test1_comp.mp4" controls></video>

__Paramètres finaux de transformation :__
- Angle de rotation (radians) : -0.00463
- Translation (x, y, z) : (-0.01, 0.00, -1.84)
- Nombre d'itérations :  20
- Valeur finale de la métrique :  28735.10959828842


Nous pouvons constater que le résultat est assez mauvais, probablement en raison de l'inclusion d'une transformation de rotation.

### Test n°2: TranslationTransform

Au lieu de cela, nous avons opté pour l'application d'une translation.

**Description:** Translation d'un espace de coordonnées 2D ou 3D.

**Analyse:**

<video src="images/translation_test1.mp4" controls></video>

- optimizer.SetLearningRate(4.0)
- optimizer.SetMinimumStepLength(0.001)
- optimizer.SetNumberOfIterations(500)

__Paramètres finaux de transformation :__
Translation (x, y, z) : (-0.83, -3.54, -59.46)
Nombre d'itérations :  20
Valeur finale de la métrique :  11180.776647271514

On peut voir que le résultat final est beaucoup meilleur, également indiqué par la valeur finale de l'optimizer qui a été coupé en deux.

Néanmois, on a testé de changer les paramètres de l'optimizer pour voir si on pouvait encore amellioré le score:

**TEST 1:** augmenter iterations
- optimizer.SetLearningRate(4.0)
- optimizer.SetMinimumStepLength(0.00001)
- optimizer.SetNumberOfIterations(500)

__Paramètres finaux de transformation :__
Translation (x, y, z) : (-0.83, -3.54, -59.46)
Nombre d'itérations :  32
Valeur finale de la métrique :  11180.21821197873


**TEST 2:** Réduire le learning rate
- optimizer.SetLearningRate(1.0)
- optimizer.SetMinimumStepLength(0.00001)
- optimizer.SetNumberOfIterations(200)

__Paramètres finaux de transformation :__
Translation (x, y, z) : (-0.83, -3.54, -59.46)
Nombre d'itérations :  27
Valeur finale de la métrique :  11180.221791522592

Ces changements n'apportent que une très petit réduction du score.

## Segmentation des tumeurs
**A compléter**, utiliser la lib itk
 - Méthode utilisée
 - Pourquoi cette méthodes
 - Les Difficultés rencontrées
 - Le résultat

## Analyse et visualisation
**A compléter**, utiliser la lib vtk
 - Methodes de calcul des différences de volume, forme, position entre 2 tumeurs
 - Méthode de visualisation
 - Guide et fonctionnement

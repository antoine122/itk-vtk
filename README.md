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
Antoine HAVARD : Recadrage, architecture

Emma CASAGRANDE : Recadrage

Salomé BERGER : Visualisation

Corentin COLMEL : Segmentation

## Recalage d'images

Pour recalé **l'image 2** sur **l'image 1**, on à suivi cette pipeline de traitement :
![img recadrage](bin/methode_de_recadrage.png)

### Algorithme pour la métrique
 - **MeanSquaresImageToImageMetricv4** : Calcule la moyenne des carrés des différences d’intensité entre les deux images. Plus la différence est faible, plus l’alignement est bon.

 - **CorrelationImageToImageMetricv4** : Calcule la corrélation linéaire entre les intensités des deux images.

**MeanSquaresImageToImageMetricv4** est bien adaptée car les deux images IRM ont une intensité comparable voxel par voxel. Elle donne des résultats rapides et stables dans ce contexte homogène.


### Algorithme pour l'optimiseur
 - **RegularStepGradientDescentOptimizerv4** : Descente de gradient avec un pas régulier qui diminue progressivement.

 - **GradientDescentOptimizerv4** : Descente de gradient classique avec un pas fixe.

 - **AmoebaOptimizerv4** : Méthode de Nelder-Mead, sans utiliser de dérivées.

**RegularStepGradientDescentOptimizerv4**  converge bien et est plus tolérant au bruit. D’autres méthodes comme Amoeba ou GradientDescent étaient soit trop sensibles aux paramètres initiaux, soit plus lentes à converger.


### Algorithme pour la transformation

Pour la transformation, nous avons regarder 2 grand cas :

#### Test n°1: VersorRigid3DTransform

Pour commencer, on a voulu tester de faire un recalage en appliquant une translation et une rotation. Pour cela on a utilisé VersorRigid3DTransform
qui fonctionnait bien avec des images médicales en 3D.

**Description:** VersorRigid3DTransform applique une rotation et une translation à l'espace.

**Analyse:**

- __Image Gauche__: Fixed Image
- __Image Milieu__: Moving Image
- __Image Droite__: Résultat

![Aperçu en gif1](bin/test1_comp.gif)

__Paramètres finaux de transformation :__
- Angle de rotation (radians) : -0.00463
- Translation (x, y, z) : (-0.01, 0.00, -1.84)
- Nombre d'itérations :  20
- Valeur finale de la métrique :  28735.10959828842


Nous pouvons constater que le résultat est assez mauvais, probablement en raison de l'inclusion d'une transformation de rotation.

#### Test n°2: TranslationTransform

Au lieu de cela, nous avons opté pour l'application d'une translation.

**Description:** Translation d'un espace de coordonnées 2D ou 3D.

**Analyse:**

![Aperçu en gif2](bin/translation_test1.gif)

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

### récapitulatif des fonction utilisé

| Méthode            | Algorithme                              | Utilité                                                                      | Justification du choix                                                                           |
| :----------------: | :-------------------------------------: | :--------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------: |
| **Transformation** | `TranslationTransform`                  | Modélise un simple décalage en X, Y, Z                                       | Les images proviennent du même patient, sans rotation ni déformation importante              |
| **Optimisation**   | `RegularStepGradientDescentOptimizerv4` | Cherche les meilleurs paramètres de transformation en minimisant la métrique | Méthode simple, stable et efficace pour des problèmes bien posés comme notre cas                       |
| **Métrique**       | `MeanSquaresImageToImageMetricv4`       | Compare directement les intensités voxel à voxel entre les deux images       | Les images étant de même modalité et contraste, la comparaison d’intensité est adaptée et rapide |


## Segmentation des tumeurs

La segmentation se fait en deux parties :

### 1. Adoucir l'image

Cette étape a pour but de réduire le bruit dans la tumeur et de flouter la forme de la tumeur pour éviter les imprécisions.

Nous avons utilisé la fonction [`itk.CurvatureFlowImageFilter`](https://docs.itk.org/projects/doxygen/en/stable/classitk_1_1CurvatureFlowImageFilter.html).

---

### 2. Seuillage connecté

Ce seuillage commence à une position choisie et vérifie pour chaque voisin s'il est entre les seuils inférieur et supérieur.  
L'algorithme se propage ainsi et marque toutes les positions par lesquelles il passe.

À partir de nos observations, nous avons décidé d'utiliser :

- La position de départ : `(90, 70, 51)`
- Les seuils : `500` (inférieur) et `800` (supérieur)

La fonction utilisée pour cet algorithme est [`itk.ConnectedThresholdImageFilter`](https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1ConnectedThresholdImageFilter.html).

---

Avec cet algorithme, nous avons délimité la zone de la tumeur. Voici les résultats :

#### Résultat pour l'image 1 :

![résultats image1](bin/seg1.png)

#### Résultat pour l'image 2 (recalée) :

![résultats image1](bin/seg2.png)

## Visualisation

Cette partie repose sur l'utilisation de la bibliothèque VTK pour visualiser les volumes segmentés et mettre en évidence leur évolution dans le temps.

### Méthodes de calcul des différences

À partir des deux segmentations binaires de la tumeur (images ITK `itk_seg1` et `itk_seg2`), le code procède à :

* **Un calcul de volume** pour chaque segmentation :
  Le volume est obtenu en multipliant le nombre de voxels segmentés par le volume élémentaire d’un voxel (produit des espacements dans chaque direction).

* **Une comparaison voxel à voxel** :

  * Les voxels présents dans `itk_seg2` mais absents de `itk_seg1` sont considérés comme une **croissance** tumorale.
  * Les voxels présents dans `itk_seg1` mais absents de `itk_seg2` sont considérés comme une **réduction** tumorale.

* **Affichage des statistiques** :

  * Volume de la tumeur au temps 1 et au temps 2
  * Croissance en volume (mm³)
  * Réduction en volume (mm³)
  * Différence nette (gain ou perte total)

### Méthode de visualisation

L'affichage 3D repose sur plusieurs étapes :

1. **Conversion des images ITK en images VTK** :
   Une conversion mémoire est réalisée pour permettre à VTK d'accéder directement aux données segmentées.

2. **Extraction de surface par `vtkMarchingCubes`** :
   Chaque volume binaire est transformé en surface polygonale 3D (isosurface) pour en faciliter la représentation.

3. **Lissage des maillages avec `vtkSmoothPolyDataFilter`** :
   Les surfaces générées sont filtrées pour éliminer l'effet de “voxelisation” en appliquant un lissage itératif non réducteur.

4. **Affichage des différents volumes** :

   * **Tumeur au temps 1** : rouge transparent
   * **Tumeur au temps 2** : vert transparent
   * **Croissance (voxels nouveaux)** : cyan opaque
   * **Réduction (voxels disparus)** : magenta opaque

5. **Texte à l’écran** :
   Un objet `vtkTextActor` est utilisé pour afficher les volumes mesurés, la variation totale ainsi que les volumes de croissance et de réduction.

### Fonctionnement et guide d'utilisation

La visualisation se fait via la fonction `show_surfaces(itk_seg1, itk_seg2)`, qui reçoit deux images ITK binaires (segmentations de la tumeur à deux dates) et affiche une scène interactive avec :

* Rotation et zoom possibles à la souris
* Mise en évidence directe des différences spatiales
* Affichage des métriques de comparaison

Cette approche permet une **analyse conjointe quantitative et qualitative** de l’évolution tumorale, dans un référentiel spatial commun (les deux images ayant été préalablement recalées).

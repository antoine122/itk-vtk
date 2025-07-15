import os
import sys

import itk
import registration
import segmentation
import visualization

PATH_DATA = "Data/"
PATH_TUMEUR1 = "case6_gre1.nrrd"
PATH_TUMEUR2 = "case6_gre2.nrrd"


def main():
    # Load data
    print("Chargement des données...")
    curr_path = os.path.dirname(__file__)

    img_tumeur1 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR1), pixel_type=itk.F)
    img_tumeur2 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR2), pixel_type=itk.F)

    img_tumeur2_align = registration.recalage(img_tumeur1, img_tumeur2)
   
    # Cropping and registration data
    print("Recalage des 2 scan...")
    # TODO

    # Segmentation data
    print("Segmentation...")
    # TODO

    # Visualisation and interface
    print("Visualisation...")
    # TODO

if __name__ == "__main__":
    main()

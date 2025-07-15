import os
import sys

import itk
import registration
import segmentation
import visualization


import SimpleITK as sitk
import napari

PATH_DATA = "Data/"
PATH_TUMEUR1 = "case6_gre1.nrrd"
PATH_TUMEUR2 = "case6_gre2.nrrd"

##### FONCTIONS UTILES #####
def display_image(img):
    image_np = sitk.GetArrayViewFromImage(img)
    viewer = napari.view_image(image_np, name='Tumor Image', colormap='gray')
    napari.run()


##### RECALAGE #####

def recalage(fixed_image, moving_image):
    TransformType = itk.VersorRigid3DTransform[itk.D]
    initialTransform = TransformType.New()

    dimension = fixed_image.GetImageDimension()
    FixedImageType = type(fixed_image)
    print(f"fixed image type: {FixedImageType}")
    MovingImageType = type(moving_image)
    print(f"moving image type: {MovingImageType}")

    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
    optimizer.SetLearningRate(1)
    optimizer.SetMinimumStepLength(1e-6)
    optimizer.SetNumberOfIterations(100)

    metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()

    registration = itk.ImageRegistrationMethodv4[FixedImageType, MovingImageType].New(FixedImage=fixed_image, MovingImage=moving_image, Metric=metric,
                                                        Optimizer=optimizer, InitialTransform=initialTransform)

    print("Début de recalage...")
    registration.Update()
    print("Recalage terminé!")

    transform = registration.GetTransform()
    final_parameters = transform.GetParameters()
    angle = final_parameters.GetElement(0)
    translation_along_x = final_parameters.GetElement(1)
    translation_along_y = final_parameters.GetElement(2)

    number_of_iterations = optimizer.GetCurrentIteration()

    best_value = optimizer.GetValue()

    print("Result = ")
    print(" Translation X = " + str(translation_along_x))
    print(" Translation Y = " + str(translation_along_y))
    print(" Iterations    = " + str(number_of_iterations))
    print(" Metric value  = " + str(best_value))

##### SEGMENTATION #####



def main():
    # Load data
    print("Chargement des données...")
    curr_path = os.path.dirname(__file__)

    img_tumeur1 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR1), pixel_type=itk.F)
    img_tumeur2 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR2), pixel_type=itk.F)

    recalage(img_tumeur1, img_tumeur2)
    # display_image(sitk.ReadImage(os.path.join(curr_path, PATH_DATA, PATH_TUMEUR1)))
   
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

import itk
import matplotlib.pyplot as plt
import os
import numpy as np
#objectif : trouver les valeures basses et hautes des tumeurs dans nos photos
# s'assurer que les images sont du bon data type
# smooth les images
# faire un threshold avec une connectivité sur les images smooth

def segment(image1, image2, seed, imgType):
    #Les images ont déjà le bon datatype

    #Smooth both images
    smoother = itk.CurvatureFlowImageFilter.New(Input=image1)
    smoother.SetTimeStep(0.125)
    smoother.SetNumberOfIterations(5)
    smoother.Update()
    image1Smoothed = smoother.GetOutput()

    smoother = itk.CurvatureFlowImageFilter.New(Input=image2)
    smoother.SetTimeStep(0.125)
    smoother.SetNumberOfIterations(5)
    smoother.Update()
    image2Smoothed = smoother.GetOutput()

    threshold = itk.ConnectedThresholdImageFilter[imgType, imgType].New()
    
    threshold.SetInput(image1Smoothed)

    lbound = 500
    ubound = 800
    threshold.SetLower(lbound)
    threshold.SetUpper(ubound)

    threshold.SetReplaceValue(255)
    threshold.SetSeed(seed)
    threshold.Update()

    image1Seg = threshold.GetOutput()

    threshold = itk.ConnectedThresholdImageFilter[imgType, imgType].New()
    threshold.SetInput(image2Smoothed)
    threshold.SetLower(lbound)
    threshold.SetUpper(ubound)

    threshold.SetReplaceValue(255)
    threshold.SetSeed(seed)
    threshold.Update()
    image2Seg = threshold.GetOutput()

    # print("showing images")
    fig, axes = plt.subplots(3, 2, figsize=(8, 10))
    axes[0, 0].imshow(image2[seed[0] - 35, :, :], cmap='gray')
    axes[0, 1].imshow(image2Seg[seed[0] - 35, :, :], cmap='gray')
    axes[1, 0].imshow(image2[:, seed[1], :], cmap='gray')
    axes[1, 1].imshow(image2Seg[:, seed[1], :], cmap='gray')
    axes[2, 0].imshow(image2[:, :, seed[2] + 30], cmap='gray')
    axes[2, 1].imshow(image2Seg[:, :, seed[2] + 30], cmap='gray')
    plt.show()

    return (image1Seg, image2Seg)


if __name__ == "__main__":
    PATH_DATA = "Data/"
    PATH_TUMEUR1 = "case6_gre1.nrrd"
    PATH_TUMEUR2 = "case6_gre2_registered.nrrd"

    curr_path = os.path.dirname(__file__)

    print("Chargement des images...")
    PixelType = itk.D
    img1 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR1), pixel_type=PixelType)
    img2 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR2), pixel_type=PixelType)

    segment(img1,  img2, (90,70,51), itk.Image[itk.D, 3])

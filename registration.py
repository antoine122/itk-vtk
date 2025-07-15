import os
import sys

import itk

def recalage(fixed_image, moving_image):
    # Info
    PixelType = itk.D
    dimension = fixed_image.GetImageDimension() # 3
    ImageType = itk.Image[PixelType, dimension]

    """
    FixedImageType = type(fixed_image)
    MovingImageType = type(moving_image)
    """

    # Transformation
    TransformType = itk.VersorRigid3DTransform[PixelType]
    initialTransform = TransformType.New()

    # initialisation centrée de la transformation
    initializerType = itk.CenteredTransformInitializer[
        TransformType, ImageType, ImageType
    ]
    initializer = initializerType.New(
        Transform=initialTransform,
        FixedImage=fixed_image,
        MovingImage=moving_image
    )
    initializer.InitializeTransform()

    # Optimisation
    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()

    optimizer.SetLearningRate(4.0)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetNumberOfIterations(200)

    # Metric
    metric = itk.MeanSquaresImageToImageMetricv4[ImageType, ImageType].New()

    # Redimention
    registration = itk.ImageRegistrationMethodv4[ImageType, ImageType].New()
    registration.SetFixedImage(fixed_image)
    registration.SetMovingImage(moving_image)
    registration.SetMetric(metric)
    registration.SetOptimizer(optimizer)
    registration.SetInitialTransform(initialTransform)
    registration.InPlaceOn()

    # Transformation
    print("Début de recalage...")
    registration.Update()
    print("Recalage terminé!")

    transform = registration.GetModifiableTransform()
    parameters = transform.GetParameters()

    print("Paramètres finaux de transformation :")
    print("Angle de rotation (radians) : {:.5f}".format(parameters[0]))
    print("Translation (x, y, z) : ({:.2f}, {:.2f}, {:.2f})".format(parameters[1], parameters[2], parameters[3]))
    print("Nombre d'itérations : ", optimizer.GetCurrentIteration())
    print("Valeur finale de la métrique : ", optimizer.GetValue())

    # Application de la transformation sur l'image mobile
    resampler = itk.ResampleImageFilter[ImageType, ImageType].New()
    resampler.SetInput(moving_image)
    resampler.SetTransform(transform)
    resampler.SetSize(fixed_image.GetLargestPossibleRegion().GetSize())
    resampler.SetOutputOrigin(fixed_image.GetOrigin())
    resampler.SetOutputSpacing(fixed_image.GetSpacing())
    resampler.SetOutputDirection(fixed_image.GetDirection())
    resampler.SetDefaultPixelValue(0)

    print("Application de la transformation à l'image mobile...")
    resampler.Update()
    return resampler.GetOutput()


if __name__ == "__main__":
    import SimpleITK as sitk
    import napari

    def display_image(img):
        image_np = sitk.GetArrayViewFromImage(img)
        viewer = napari.view_image(image_np, name='Tumor Image', colormap='gray')
        napari.run()
    
    PATH_DATA = "Data/"
    PATH_TUMEUR1 = "case6_gre1.nrrd"
    PATH_TUMEUR2 = "case6_gre2.nrrd"

    curr_path = os.path.dirname(__file__)

    print("Chargement des images...")
    PixelType = itk.D
    img1 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR1), pixel_type=PixelType)
    img2 = itk.imread(os.path.join(curr_path, PATH_DATA + PATH_TUMEUR2), pixel_type=PixelType)

    print("recadrage...")
    img2_registered = recalage(img1, img2)

    print("Téléchargement de l'image 2 recadrée dans 'case6_gre2_registered.nrrd'...")
    output_path = os.path.join(curr_path, PATH_DATA, "case6_gre2_registered.nrrd")
    itk.imwrite(img2_registered, output_path)

    #print("affichage du resultat...")
    #display_image(sitk.ReadImage(os.path.join(curr_path, PATH_DATA, PATH_TUMEUR1)))

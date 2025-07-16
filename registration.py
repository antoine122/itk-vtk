import os
import sys

import itk

"""
def recalage(fixed_image, moving_image):
    # Info
    PixelType = itk.D
    dimension = fixed_image.GetImageDimension() # 3
    ImageType = itk.Image[PixelType, dimension]

    # Transformation
    print("Création de la Transform")
    TransformType = itk.VersorRigid3DTransform[PixelType]
    initialTransform = TransformType.New()

    print("initialisation centrée de la transformation")
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
    print("Optimisation...")
    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()

    optimizer.SetLearningRate(4.0)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetNumberOfIterations(200)

    # Metric
    print("Metric...")
    metric = itk.MeanSquaresImageToImageMetricv4[ImageType, ImageType].New()

    # Redimension
    print("Redimension...")
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
"""

def init_transform(PixelType, dimension):
    print("Création de la Transform")
    TransformType = itk.TranslationTransform[PixelType, dimension]
    initialTransform = TransformType.New()
    return TransformType, initialTransform


def init_optimizer():
    print("optimisation...")
    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
    optimizer.SetLearningRate(1.0)
    optimizer.SetMinimumStepLength(0.000001)
    optimizer.SetNumberOfIterations(200)
    return optimizer


def init_metric(ImageType):
    print("Metric...")
    metric = itk.MeanSquaresImageToImageMetricv4[ImageType, ImageType].New()
    return metric


def init_registration(fixed_image, moving_image, metric, optimizer, initialTransform, ImageType):
    print("Init Registration...")
    registration = itk.ImageRegistrationMethodv4[ImageType, ImageType].New(
        FixedImage=fixed_image,
        MovingImage=moving_image,
        Metric=metric,
        Optimizer=optimizer, 
        InitialTransform=initialTransform
    )
    return registration


def apply_transform(fixed_image, moving_image, registration, ImageType):
    transform = registration.GetModifiableTransform()
    parameters = transform.GetParameters()
    print("Translation (x, y, z) : ({:.2f}, {:.2f}, {:.2f})".format(parameters[0], parameters[1], parameters[2]))
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
    return resampler


def recalage(fixed_image, moving_image):
    # Info
    PixelType = itk.D
    dimension = fixed_image.GetImageDimension() # 3
    ImageType = itk.Image[PixelType, dimension]

    # Transformation
    TransformType, initialTransform = init_transform(PixelType, dimension)
    # Optimisation
    optimizer = init_optimizer()
    # Metric
    metric = init_metric(ImageType)
    # Init Registration
    registration = init_registration(fixed_image, moving_image, metric, optimizer, initialTransform, ImageType)

    # initialisation centrée de la transformation
    print("initialisation centrée de la transformation...")
    moving_initial_transform = TransformType.New()
    initial_parameters = moving_initial_transform.GetParameters()
    initial_parameters[0] = 0
    initial_parameters[1] = 0
    moving_initial_transform.SetParameters(initial_parameters)

    registration.SetMovingInitialTransform(moving_initial_transform)

    # Transformation
    print("Début de recalage...")
    registration.Update()
    print("Recalage terminé!")

    # Application de la transformation sur l'image mobile
    print("Paramètres finaux de transformation :")
    print("Nombre d'itérations : ", optimizer.GetCurrentIteration())
    print("Valeur finale de la métrique : ", optimizer.GetValue())
    resampler = apply_transform(fixed_image, moving_image, registration, ImageType)
    return resampler.GetOutput()


if __name__ == "__main__":
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

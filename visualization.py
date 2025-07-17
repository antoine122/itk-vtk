import itk
import vtk
import numpy as np

def itk_to_vtk_image(itk_image):
    itk_array = itk.GetArrayFromImage(itk_image).astype(np.uint8)
    shape = itk_array.shape

    importer = vtk.vtkImageImport()
    data_string = itk_array.tobytes()
    importer.CopyImportVoidPointer(data_string, len(data_string))

    importer.SetDataScalarTypeToUnsignedChar()
    importer.SetNumberOfScalarComponents(1)

    importer.SetWholeExtent(0, shape[2]-1, 0, shape[1]-1, 0, shape[0]-1)
    importer.SetDataExtentToWholeExtent()
    importer.Update()

    return importer.GetOutput()

def create_surface(image_vtk, color, opacity=1.0):
    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(image_vtk)
    surface.SetValue(0, 128)
    surface.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)
    return actor

def compute_volume(itk_image):
    array = itk.GetArrayFromImage(itk_image)
    voxel_volume = np.prod(itk_image.GetSpacing())
    return np.sum(array > 0) * voxel_volume

def compute_difference_image(itk_seg1, itk_seg2):
    arr1 = itk.GetArrayFromImage(itk_seg1).astype(bool)
    arr2 = itk.GetArrayFromImage(itk_seg2).astype(bool)
    
    added = np.logical_and(arr2, np.logical_not(arr1))
    removed = np.logical_and(arr1, np.logical_not(arr2))
    
    diff_array = np.zeros_like(arr1, dtype=np.uint8)
    diff_array[added] = 1
    diff_array[removed] = 2

    diff_itk = itk.GetImageFromArray(diff_array)
    diff_itk.CopyInformation(itk_seg1)
    return diff_itk

def create_diff_surface(vtk_image, label_value, color, opacity):
    thresh = vtk.vtkImageThreshold()
    thresh.SetInputData(vtk_image)
    thresh.ThresholdBetween(label_value, label_value)
    thresh.SetInValue(255)
    thresh.SetOutValue(0)
    thresh.Update()

    return create_surface(thresh.GetOutput(), color=color, opacity=opacity)

def show_surfaces(itk_seg1, itk_seg2):
    # Conversion ITK -> VTK
    vtk_img1 = itk_to_vtk_image(itk_seg1)
    # vtk_img2 = itk_to_vtk_image(itk_seg2)

    # Acteurs des segmentations originales
    actor1 = create_surface(vtk_img1, color=(1, 0, 0), opacity=0.3)  # Rouge
    # actor2 = create_surface(vtk_img2, color=(0, 1, 0), opacity=0.3)  # Vert

    # Calcul des volumes
    arr1 = itk.GetArrayFromImage(itk_seg1).astype(bool)
    arr2 = itk.GetArrayFromImage(itk_seg2).astype(bool)
    voxel_volume = np.prod(itk_seg1.GetSpacing())

    vol1 = np.sum(arr1) * voxel_volume
    vol2 = np.sum(arr2) * voxel_volume
    delta = vol2 - vol1

    # Calcul des régions de croissance et de réduction
    growth_mask = np.logical_and(arr2, np.logical_not(arr1))
    reduction_mask = np.logical_and(arr1, np.logical_not(arr2))

    growth_vol = np.sum(growth_mask) * voxel_volume
    reduction_vol = np.sum(reduction_mask) * voxel_volume

    # Création de l'image des différences
    diff_array = np.zeros_like(arr1, dtype=np.uint8)
    diff_array[growth_mask] = 1
    diff_array[reduction_mask] = 2

    diff_itk = itk.GetImageFromArray(diff_array)
    diff_itk.CopyInformation(itk_seg1)
    vtk_diff = itk_to_vtk_image(diff_itk)

    # Acteurs pour les différences
    actor_growth = create_diff_surface(vtk_diff, 1, color=(0, 1, 1), opacity=1.0)     # Cyan = croissance
    actor_reduction = create_diff_surface(vtk_diff, 2, color=(1, 0, 1), opacity=1.0)  # Magenta = réduction

    # Texte des volumes
    volume_text = (
        f"Tumeur 1 : {vol1:.2f} mm³\n"
        f"Tumeur 2 : {vol2:.2f} mm³\n"
        f"Δ volume : {delta:+.2f} mm³\n"
        f"Croissance : {growth_vol:.2f} mm³\n"
        f"Réduction : {reduction_vol:.2f} mm³"
    )

    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(volume_text)
    text_actor.GetTextProperty().SetFontSize(20)
    text_actor.GetTextProperty().SetColor(1, 1, 1)
    text_actor.SetDisplayPosition(10, 10)

    # Rendu
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor1)
    # renderer.AddActor(actor2)
    renderer.AddActor(actor_growth)
    renderer.AddActor(actor_reduction)
    renderer.AddActor2D(text_actor)
    renderer.SetBackground(0.1, 0.1, 0.2)

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(800, 600)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    window.Render()
    interactor.Start()

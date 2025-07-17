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

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(opacity)
    return actor

def compute_volume(itk_image):
    array = itk.GetArrayFromImage(itk_image)
    voxel_volume = np.prod(itk_image.GetSpacing())
    return np.sum(array > 0) * voxel_volume

def show_surfaces(itk_seg1, itk_seg2):
    vtk_img1 = itk_to_vtk_image(itk_seg1)
    vtk_img2 = itk_to_vtk_image(itk_seg2)

    actor1 = create_surface(vtk_img1, color=(1, 0, 0), opacity=0.5)
    actor2 = create_surface(vtk_img2, color=(0, 1, 0), opacity=0.5)
    actor2.SetPosition(100, 0, 0)

    vol1 = compute_volume(itk_seg1)
    vol2 = compute_volume(itk_seg2)

    delta = vol2 - vol1
    volume_text = f"Tumeur 1: {vol1:.2f} mm³\nTumeur 2: {vol2:.2f} mm³\nΔ: {delta:+.2f} mm³"

    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(volume_text)
    text_actor.GetTextProperty().SetFontSize(20)
    text_actor.GetTextProperty().SetColor(1, 1, 1)
    text_actor.SetDisplayPosition(10, 10)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor1)
    renderer.AddActor(actor2)
    renderer.AddActor2D(text_actor)
    renderer.SetBackground(0.1, 0.1, 0.2)

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(800, 600)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    window.Render()
    interactor.Start()

import pyg4ometry
import vtk
import sys


filename = sys.argv[1]
r = pyg4ometry.gdml.Reader(f"C:/Users/david/Documents/TRIUMF/projects/3DRM-design/cad/2nd try/gdmls/{filename}.gdml")
volume = r.getRegistry().getWorldVolume()

m = volume.mesh.getLocalMesh()
vtkConverter = vtk.Converter()
vtkPD =  pyg4ometry.vtkConverter.MeshListToPolyData(m)
r = pyg4ometry.vtk.WriteSTL("file.stl",vtkPD)
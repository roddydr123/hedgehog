import pyg4ometry
import sys
import vtk as _vtk
from weightsCone import path


def writeVtkPolyDataAsSTLFile(fileName, meshes):
    """
    Pyg4ometry function to write an STL file from poly data.
    """
    # Convert vtkPolyData to STL mesh
    appendFilter = _vtk.vtkAppendPolyData()

    for m in meshes:
        if m:
            appendFilter.AddInputData(m)
            appendFilter.Update()

    # remove duplicate points
    cleanFilter = _vtk.vtkCleanPolyData()
    cleanFilter.SetInputConnection(appendFilter.GetOutputPort())
    cleanFilter.Update()

    # write STL file
    stlWriter = _vtk.vtkSTLWriter()
    stlWriter.SetFileName(fileName)
    stlWriter.SetInputConnection(appendFilter.GetOutputPort())
    stlWriter.Write()
    return stlWriter


def convert(filename=None):
    """
    Converts a geometry from GDML format to STL format.
    """

    if not filename:
        filename = sys.argv[1]

    print("reading...")
    r = pyg4ometry.gdml.Reader(f'{path}files/{filename}.gdml')
    reg = r.getRegistry()

    meshes = []

    # allows looping through logical and physical volumes simultaneously
    dualDict = zip(reg.logicalVolumeDict, reg.physicalVolumeDict)

    print("meshing...")
    for kv, kp in dualDict:
        # don't include the world volume and the water phantom in the
        # hedgehog geometry.
        if (kv != 'wl') & (kv != 'hb1_l'):
            lv = reg.logicalVolumeDict[kv]
            pv = reg.physicalVolumeDict[kp]

            # set the number of slices in the mesh around the pin
            # circumference.
            pinSolid = lv.solid
            pinSolid.nslice = 50

            mesh = lv.solid.mesh()

            # scale the pin mesh using the physical volume
            if pv.scale:
                s = pv.scale.eval()
                mesh.scale(s)
                if s[0]*s[1]*s[2] == 1:
                    pass
                elif s[0]*s[1]*s[2] == -1:
                    mesh = mesh.inverse()

            # translate the pin mesh to the right place
            t = pv.position.eval()
            mesh.translate(t)

            vtkPD = pyg4ometry.visualisation.Convert.\
                pycsgMeshToVtkPolyData(mesh)

            # make a list of meshes to be written up in one go.
            meshes.append(vtkPD)

    print("writing...")
    writeVtkPolyDataAsSTLFile(f'{path}files/{filename}.stl', meshes)


if __name__ == "__main__":
    convert()

import pyg4ometry
import sys
import vtk as _vtk


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


def convert():
    """
    Converts a geometry from GDML format to STL format.
    """

    filepath = '/mnt/c/Users/david/documents/triumf/projects/3drm-design/cad/2nd try'
    filename = sys.argv[1]

    print("reading...")
    r = pyg4ometry.gdml.Reader(f'{filepath}/gdmls/{filename}.gdml')
    reg = r.getRegistry()

    meshes = []

    # allows looping through logical and physical volumes simultaneously
    dualDict = zip(reg.logicalVolumeDict, reg.physicalVolumeDict)

    print("meshing...")
    for kv, kp in dualDict:
        # don't include the world volume and the water phantom in the
        # hedgehog geometry.
        if (kv != 'wl') & (kv != 'wa1_l'):
            lv = reg.logicalVolumeDict[kv]
            pv = reg.physicalVolumeDict[kp]

            # get the logical volume mesh but the correct scale and
            # translation from the physical volume.
            m = lv._getPhysicalDaughterMesh(pv)

            vtkPD = pyg4ometry.visualisation.Convert.pycsgMeshToVtkPolyData(m)

            # make a list of meshes to be written up in one go.
            meshes.append(vtkPD)

    print("writing...")
    w = writeVtkPolyDataAsSTLFile(f'{filepath}/stls/{filename}.stl', meshes)


if __name__ == "__main__":
    convert()

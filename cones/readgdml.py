import pyg4ometry
import sys


def display():

    filename = f'files/{sys.argv[1]}'
    reg = pyg4ometry.geant4.Registry()

    print("reading in...")
    r = pyg4ometry.gdml.Reader(f"{filename}.gdml")
    print("visualizing...")
    ls = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewer()
    v.addLogicalVolume(ls)
    v.view()


display()

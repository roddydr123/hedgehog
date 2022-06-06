import pyg4ometry
import sys
from private.private import path


def display():

    filename = f'{path}files/{sys.argv[1]}'
    pyg4ometry.geant4.Registry()

    print("reading in...")
    r = pyg4ometry.gdml.Reader(f"{filename}.gdml")
    print("visualizing...")
    ls = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewer()
    v.addLogicalVolume(ls)
    v.view()


display()

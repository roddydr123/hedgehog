import pyg4ometry
import numpy as np
import sys
import square as sq
import weightsSquare as wsq


def main():
    reg  = pyg4ometry.geant4.Registry()

    pinData = sq.optimizer()

    # create the world
    ws   = pyg4ometry.geant4.solid.Box("ws",5e6,5e6,5e6,reg)
    wl   = pyg4ometry.geant4.LogicalVolume(ws,"G4_Galactic","wl",reg)
    reg.setWorld(wl.name)

    # make the base at origin
    baseWidth = pinData["thicknesses"].min()
    baseEnd = baseWidth / 2
    b1   = pyg4ometry.geant4.solid.Box("b1",0.5,0.5,baseWidth,reg, lunit="cm")
    b1_l = pyg4ometry.geant4.LogicalVolume(b1,"G4_Fe","b1_l",reg, lunit="cm")
    b1_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[0,0,0],b1_l,"b1_p",wl,reg)

    # make the water box
    wa1   = pyg4ometry.geant4.solid.Box("wa1",500,500,100,reg, lunit="cm")
    wa1_l = pyg4ometry.geant4.LogicalVolume(wa1,"G4_Fe","wa1_l",reg, lunit="cm")
    wa1_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[0,0,510],wa1_l,"wa1_p",wl,reg)

    # create an array of locations where I want the pins to be
    pinLocArrX = np.linspace(-0.2, 0.2, 5) * 10
    pinLocArrY = np.linspace(-0.2, 0.2, 5) * 10

    # each block height is the height of the pin over the # blocks in the pin
    height = (pinData["thicknesses"].max() - baseWidth) / (len(pinData["thicknesses"]) - 1)

    # create multiple pins along an axis
    for xcoord in pinLocArrX:

        for ycoord in pinLocArrY:

            for i in range(len(pinData["edges"]) - 1):
                # make each pin block and put it in position
                z_shift = (baseEnd + (i * height) + (height/2)) * 10
                width = pinData["edges"][i]
                b2   = pyg4ometry.geant4.solid.Box(f"b2-{xcoord}-{ycoord}-{i}",width,width,height,reg, "cm")
                b2_l = pyg4ometry.geant4.LogicalVolume(b2,"G4_Fe",f"b2_l-{xcoord}-{ycoord}-{i}",reg, "cm")
                b2_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[xcoord,ycoord,z_shift],b2_l,f"b2_p-{xcoord}-{ycoord}-{i}",wl,reg)

    # write to gdml
    writer = pyg4ometry.gdml.Writer()
    writer.addDetector(reg)
    writer.write(f"files/{sys.argv[1]}.gdml")

main()

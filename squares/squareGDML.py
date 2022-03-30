import pyg4ometry
import numpy as np
import sys
from square import optimizer
from weightsSquare import d_across_pinbase, baseEdges, blockHeight


def getPinLocs():

    # create the arrays based on square pinbases
    pinLocArrX = np.arange(baseEdges * -1/2, baseEdges/2, d_across_pinbase) * 10
    pinLocArrY = np.arange(baseEdges * -1/2, baseEdges/2, d_across_pinbase) * 10

    return pinLocArrX, pinLocArrY


def main():
    reg  = pyg4ometry.geant4.Registry()

    pinData = optimizer(sys.argv[1])

    # create the world
    ws   = pyg4ometry.geant4.solid.Box("ws",5e6,5e6,5e6,reg)
    wl   = pyg4ometry.geant4.LogicalVolume(ws,"G4_Galactic","wl",reg)
    reg.setWorld(wl.name)

    # make the base at origin, get the thickness from pinData
    # set the size by the size of hedgehog we're tiling with pins
    baseThickness = pinData["thicknesses"].min()

    if baseThickness <= 0.1:
        raise ValueError("Base is too thin, please choose a shorter range SOBP")

    b1   = pyg4ometry.geant4.solid.Box("b1",baseEdges,baseEdges,baseThickness,reg, lunit="cm")
    b1_l = pyg4ometry.geant4.LogicalVolume(b1,"G4_Fe","b1_l",reg, lunit="cm")
    b1_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[0,0,0],b1_l,"b1_p",wl,reg)

    # make the water box
    water_thickness = 10
    z_disp = 1 + (water_thickness / 2)
    wa1   = pyg4ometry.geant4.solid.Box("wa1",50,50,water_thickness,reg, lunit="cm")
    wa1_l = pyg4ometry.geant4.LogicalVolume(wa1,"G4_Fe","wa1_l",reg, lunit="cm")
    wa1_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[0,0,z_disp * 10],wa1_l,"wa1_p",wl,reg)

    # fetch the pin locations
    pinLocArrX, pinLocArrY = getPinLocs()

    # to mark the progress
    no_pins = int(len(pinLocArrX) * len(pinLocArrY))
    count = 0

    # each block height is the height of the pin over the # blocks in the pin
    height = (pinData["thicknesses"].max() - baseThickness) / (len(pinData["thicknesses"]) - 1)

    # create multiple pins along an axis
    for x in pinLocArrX:

        for y in pinLocArrY:

            count = count + 1

            for q in range(len(pinData['edges']) - 1):
                # make each pin block and put it in position
                z_shift = (baseThickness / 2 + (q * height) + (height/2)) * 10
                width = pinData['edges'][q]

                b2   = pyg4ometry.geant4.solid.Box(f"b2-{x}-{y}-{q}",width,width,height,reg, lunit="cm")
                b2_l = pyg4ometry.geant4.LogicalVolume(b2,"G4_Fe",f"b2_l-{x}-{y}-{q}",reg, lunit="cm")
                b2_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[x,y,z_shift],b2_l,f"b2_p-{x}-{y}-{q}",wl,reg)

            print(f"pin #{count}/{no_pins} x: {x}, y: {y}")
    

    # write to gdml
    print("writing...")
    writer = pyg4ometry.gdml.Writer()
    writer.addDetector(reg)
    writer.write(f"files/{sys.argv[1]}.gdml")
    print("done")

if __name__=="__main__":
    main()

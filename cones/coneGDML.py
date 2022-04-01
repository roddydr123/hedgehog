import pyg4ometry
import numpy as np
import sys
from cubic import optimizer
from weightsCone import d_across_pinbase, baseEdges


def getPinLocs():
    q = 3 * d_across_pinbase / np.sqrt(3)

    # create the arrays based on hexagonal pinbases
    pinLocArrX = (np.arange(baseEdges * -1/2, baseEdges/2, q/2))
    pinLocArrY = (np.arange(baseEdges * -1/2, baseEdges/2, d_across_pinbase))

    return pinLocArrX, pinLocArrY


def main():
    reg  = pyg4ometry.geant4.Registry()

    pinData = optimizer(sys.argv[1])
    radii = pinData["radii"]
    thicknesses = pinData["thicknesses"]

    # create the world
    ws   = pyg4ometry.geant4.solid.Box("ws",5e6,5e6,5e6,reg)
    wl   = pyg4ometry.geant4.LogicalVolume(ws,"G4_Galactic","wl",reg)
    reg.setWorld(wl.name)

    # remove radii larger than small diagonal of hexagon
    nslice = radii <= (d_across_pinbase / 2)
    radii = radii[nslice]
    thicknesses = thicknesses[nslice]

    # make the base at origin, get the thickness from the thickness just larger
    # than the largest in thicknesses after above func
    baseIndex = np.where(pinData["thicknesses"] == thicknesses[0])[0][-1]
    baseThickness = pinData["thicknesses"][baseIndex - 1]

    # move pins down to meet the base at z=0
    thicknesses -= thicknesses[0]

    #if baseThickness <= 0.1:
    #    raise ValueError("Base is too thin, please choose a shorter range SOBP")

    b1   = pyg4ometry.geant4.solid.Box("b1", baseEdges, baseEdges, baseThickness, reg, lunit="cm")
    b1_l = pyg4ometry.geant4.LogicalVolume(b1,"G4_Fe","b1_l",reg, lunit="cm")
    b1_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[0,0,-(baseThickness/2)*10],b1_l,"b1_p",wl,reg)

    # make the water box
    water_thickness = 10
    z_disp = 1 + (water_thickness / 2)
    wa1   = pyg4ometry.geant4.solid.Box("wa1",50,50,water_thickness,reg, lunit="cm")
    wa1_l = pyg4ometry.geant4.LogicalVolume(wa1,"G4_Fe","wa1_l",reg, lunit="cm")
    wa1_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[0,0,z_disp * 10],wa1_l,"wa1_p",wl,reg)

    rot = np.zeros_like(pinData["radii"])

    # fetch the pin locations
    pinLocArrX, pinLocArrY = getPinLocs()

    # to mark the progress
    no_pins = int(len(pinLocArrX) * len(pinLocArrY))
    count = 0
    xrow = 1

    adj_pinLocArrY = pinLocArrY + (d_across_pinbase / 2)

    # create multiple pins along an axis
    for i, x in enumerate(pinLocArrX * 10):

        if xrow % 2 == 0:
            usingArrY = pinLocArrY
        else:
            usingArrY = adj_pinLocArrY

        xrow = xrow + 1

        for j, y in enumerate(usingArrY * 10):

            count = count + 1

            b2   = pyg4ometry.geant4.solid.Polycone(f"cone_s-{i}-{j}",0,2 * np.pi,thicknesses,rot,radii,reg, lunit="cm")
            b2_l = pyg4ometry.geant4.LogicalVolume(b2,"G4_Fe",f"cone_l-{i}-{j}",reg, lunit="cm")
            b2_p = pyg4ometry.geant4.PhysicalVolume([0,0,0],[x,y,0],b2_l,f"cone_p-{i}-{j}",wl,reg)

            print(f"pin #{count}/{no_pins} done! x: {x}, y: {y}")

    # write to gdml
    print("writing...")
    writer = pyg4ometry.gdml.Writer()
    writer.addDetector(reg)
    writer.write(f"files/{sys.argv[1]}.gdml")
    print("done")

if __name__=="__main__":
    main()

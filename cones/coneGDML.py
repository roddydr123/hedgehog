import pyg4ometry
import numpy as np
import sys
from cubic import optimizer
from weightsCone import path


def baseQuad(x):
    return x**2


def getPinLocs(d_across_pinbase, baseEdges):
    q = 3 * d_across_pinbase / np.sqrt(3)

    start = (baseEdges * -1/2) + d_across_pinbase/2
    stop = baseEdges/2 - d_across_pinbase/2

    # create the arrays based on hexagonal pinbases
    pinLocArrX = (np.arange(start, stop, q/2))
    pinLocArrY = (np.arange(start, stop, d_across_pinbase))

    return pinLocArrX, pinLocArrY


def circCheck(rad, d_across_pinbase, x, y):
    """
    Determines if a given pin is entirely within a circle of radius
    rad before allowing it to be printed.
    """

    x /= 10
    y /= 10
    pinrad = d_across_pinbase / 2
    tolerance = 1E-2

    r = np.sqrt(x**2 + y**2)
    if (r + pinrad) > (rad + tolerance):
        return False
    return True


def build(d_across_pinbase, baseEdges, filename, SOBPwidth, range, steps,
          tolerance, zsep, usrWeights, rad, pinData=None):

    if not filename:
        filename = sys.argv[1]

    reg = pyg4ometry.geant4.Registry()

    if not pinData:
        pinData = optimizer(SOBPwidth, range, steps, d_across_pinbase,
                            tolerance, zsep, usrWeights,
                            filename=filename, show=1)

    radii = pinData["radii"]
    thicknesses = pinData["thicknesses"]

    # create the world
    ws = pyg4ometry.geant4.solid.Box("ws", 5e3, 5e3, 5e3, reg)
    wl = pyg4ometry.geant4.LogicalVolume(ws, "G4_Galactic", "wl", reg)
    reg.setWorld(wl.name)

    # remove radii larger than small diagonal of hexagon
    nslice = radii <= (d_across_pinbase / 2)
    radii = radii[nslice]
    thicknesses = thicknesses[nslice]

    # make the base at origin, get the original thickness just larger
    # than the largest after the slicing above
    baseIndex = np.where(pinData["thicknesses"] == thicknesses[0])[0][-1]
    baseThickness = pinData["thicknesses"][baseIndex - 1]

    # move pins down to meet the base at z=0
    thicknesses -= thicknesses[0]

    # make air box around hedgehog
    hbox_thick = 2
    # move everything to the correct z location
    new_zero = 35.67 + 0.05

    hb1 = pyg4ometry.geant4.solid.Box("hb1", baseEdges, baseEdges,
                                      hbox_thick, reg, lunit="cm")
    hb1_l = pyg4ometry.geant4.LogicalVolume(hb1, "G4_Fe", "hb1_l", reg,
                                            lunit="cm")
    pyg4ometry.geant4.\
        PhysicalVolume([0, 0, 0],
                       [0, 0, (new_zero + (hbox_thick/2))*10],
                       hb1_l, "hb1_p", wl, reg)

    # trapezoid base
    baseWidth = baseEdges + 1

    shortCoord = (baseWidth/2 - baseThickness) * 10
    longCoord = (baseWidth/2) * 10

    # create the base object
    b1 = pyg4ometry.geant4.solid.GenericTrap("b1", shortCoord, shortCoord,
                                             shortCoord, -shortCoord,
                                             -shortCoord, -shortCoord,
                                             -shortCoord, shortCoord,
                                             longCoord, longCoord,
                                             longCoord, -longCoord,
                                             -longCoord, -longCoord,
                                             -longCoord, longCoord,
                                             baseThickness * 5, reg,
                                             lunit="cm")
    b1_l = pyg4ometry.geant4.LogicalVolume(b1, "G4_Fe", "b1_l", reg,
                                           lunit="cm")
    pyg4ometry.geant4.PhysicalVolume([0, 0, 0],
                                     [0, 0, (baseThickness/2 -
                                             hbox_thick/2)*10],
                                     b1_l, "b1_p", hb1_l, reg)

    rot = np.zeros_like(pinData["radii"])

    # fetch the pin locations
    pinLocArrX, pinLocArrY = getPinLocs(d_across_pinbase, baseEdges)

    # to mark the progress
    no_pins = int(len(pinLocArrX) * len(pinLocArrY))
    count = 0
    xrow = 1

    adj_pinLocArrY = pinLocArrY + (d_across_pinbase / 2)

    # create multiple pins along an axis
    for i, x in enumerate(np.round(pinLocArrX, 5) * 10):

        if xrow % 2 == 0:
            usingArrY = pinLocArrY
        else:
            usingArrY = adj_pinLocArrY

        xrow = xrow + 1

        # the factor of 10 is there to correct the units, there are a few
        # rogue factors of 10 around to account for this.
        for j, y in enumerate(np.round(usingArrY, 5) * 10):

            count = count + 1

            # shift pin up by correct amount (NOT IMPLEMENTED)
            # BshiftX = 0  # baseQuad((x + d_across_pinbase/2) / 10)
            shift_thick = thicknesses  # + BshiftX

            if circCheck(rad, d_across_pinbase, x, y):

                b2 = pyg4ometry.geant4.\
                    solid.Polycone(f"cone_s-{i}-{j}", 0, 2 * np.pi,
                                   shift_thick, rot, radii, reg, lunit="cm")
                b2_l = pyg4ometry.geant4.\
                    LogicalVolume(b2, "G4_Fe", f"cone_l-{i}-{j}", reg,
                                  lunit="cm")
                pyg4ometry.geant4.\
                    PhysicalVolume([0, 0, 0], [x, y, (- hbox_thick/2 +
                                                      baseThickness)*10],
                                  b2_l, f"cone_p-{i}-{j}", hb1_l, reg)

                print(f"{np.round(count * 100 / no_pins, 1)}"
                      f"% complete, pin at x: {x/10}, y: {y/10}")

    print('100% complete')
    print("writing...")
    writer = pyg4ometry.gdml.Writer()
    # this is how pyg4ometry does writing to a file...
    writer.addDetector(reg)
    writer.write(f"{path}files/{filename}.gdml")
    print("done")


def buildreverse(d_across_pinbase, baseEdges, filename, SOBPwidth, range, steps,
                 tolerance, zsep, usrWeights, rad, pinData=None):

    if not filename:
        filename = sys.argv[1]

    reg = pyg4ometry.geant4.Registry()

    if not pinData:
        pinData = optimizer(SOBPwidth, range, steps, d_across_pinbase,
                            tolerance, zsep, usrWeights,
                            filename=filename, show=1)

    radii = pinData["radii"]
    thicknesses = pinData["thicknesses"]

    # create the world
    ws = pyg4ometry.geant4.solid.Box("ws", 5e3, 5e3, 5e3, reg)
    wl = pyg4ometry.geant4.LogicalVolume(ws, "G4_Galactic", "wl", reg)
    reg.setWorld(wl.name)

    # remove radii larger than small diagonal of hexagon
    nslice = radii <= (d_across_pinbase / 2)
    radii = radii[nslice]
    thicknesses = thicknesses[nslice]

    # make the base at origin, get the original thickness just larger
    # than the largest after the slicing above
    baseIndex = np.where(pinData["thicknesses"] == thicknesses[0])[0][-1]
    baseThickness = pinData["thicknesses"][baseIndex - 1]

    # move pins down to meet the base at z=0
    thicknesses -= thicknesses[0]

    # make air box around hedgehog
    hbox_thick = 2
    # move everything to the correct z location
    #new_zero = 35.67 + 0.05
    new_zero = 30.59 - 0.05 - hbox_thick

    hb1 = pyg4ometry.geant4.solid.Box("hb1", baseEdges, baseEdges,
                                      hbox_thick, reg, lunit="cm")
    hb1_l = pyg4ometry.geant4.LogicalVolume(hb1, "G4_Fe", "hb1_l", reg,
                                            lunit="cm")
    pyg4ometry.geant4.\
        PhysicalVolume([0, 0, 0],
                       [0, 0, (new_zero + (hbox_thick/2))*10],
                       hb1_l, "hb1_p", wl, reg)

    # create the base object
    b1 = pyg4ometry.geant4.solid.Box("b1", baseEdges, baseEdges,
                                     baseThickness, reg, lunit="cm")
    b1_l = pyg4ometry.geant4.LogicalVolume(b1, "G4_Fe", "b1_l", reg,
                                           lunit="cm")
    pyg4ometry.geant4.PhysicalVolume([0, 0, 0],
                                     [0, 0, (-baseThickness/2 +
                                             hbox_thick/2)*10],
                                     b1_l, "b1_p", hb1_l, reg)

    rot = np.zeros_like(pinData["radii"])

    # fetch the pin locations
    pinLocArrX, pinLocArrY = getPinLocs(d_across_pinbase, baseEdges)

    # to mark the progress
    no_pins = int(len(pinLocArrX) * len(pinLocArrY))
    count = 0
    xrow = 1

    adj_pinLocArrY = pinLocArrY + (d_across_pinbase / 2)

    # create multiple pins along an axis
    for i, x in enumerate(np.round(pinLocArrX, 5) * 10):

        if xrow % 2 == 0:
            usingArrY = pinLocArrY
        else:
            usingArrY = adj_pinLocArrY

        xrow = xrow + 1

        # the factor of 10 is there to correct the units, there are a few
        # rogue factors of 10 around to account for this.
        for j, y in enumerate(np.round(usingArrY, 5) * 10):

            count = count + 1

            # shift pin up by correct amount (NOT IMPLEMENTED)
            # BshiftX = 0  # baseQuad((x + d_across_pinbase/2) / 10)
            shift_thick = thicknesses  # + BshiftX

            if circCheck(rad, d_across_pinbase, x, y):

                b2 = pyg4ometry.geant4.\
                    solid.Polycone(f"cone_s-{i}-{j}", 0, 2 * np.pi,
                                   shift_thick, rot, radii, reg, lunit="cm")
                b2_l = pyg4ometry.geant4.\
                    LogicalVolume(b2, "G4_Fe", f"cone_l-{i}-{j}", reg,
                                  lunit="cm")
                pyg4ometry.geant4.\
                    PhysicalVolume([np.pi, 0, 0],
                                   [x, y, (hbox_thick/2 - baseThickness)*10],
                                   b2_l, f"cone_p-{i}-{j}", hb1_l, reg)

                print(f"{np.round(count * 100 / no_pins, 1)}"
                      f"% complete, pin at x: {x/10}, y: {y/10}")

    print('100% complete')
    print("writing...")
    writer = pyg4ometry.gdml.Writer()
    # this is how pyg4ometry does writing to a file...
    writer.addDetector(reg)
    writer.write(f"{path}files/{filename}.gdml")
    print("done")


if __name__ == "__main__":
    build()

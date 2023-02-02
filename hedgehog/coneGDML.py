import pyg4ometry
import numpy as np
import sys
from cubic import optimizer


def getPinLocs(d_across_pinbase, baseEdges):
    """Finds locations to place pins which will tile the HEDGEHOG base surface.

    Args:
        d_across_pinbase (float): Diameter across the base or each pin.
        baseEdges (float): Length along the shortest side of the base when viewed from above.

    Returns:
        numpy array: Two numpy arrays describing the pin locations in x and y.
    """
    q = 3 * d_across_pinbase / np.sqrt(3)

    start = (baseEdges * -1/2) + d_across_pinbase/2
    stop = baseEdges/2 - d_across_pinbase/2

    # create the arrays based on hexagonal pinbases
    pinLocArrX = (np.arange(start, stop, q/2))
    pinLocArrY = (np.arange(start, stop, d_across_pinbase))

    return pinLocArrX, pinLocArrY


def circCheck(rad, d_across_pinbase, x, y):
    """Determines if a given pin is entirely within a circle of radius
    rad before allowing it to be printed.

    Args:
        rad (float): Radius from centre of HEDGEHOG base within pins should be placed.
        d_across_pinbase (float): Diameter across the base of each pin.
        x (float): Location of a given pin along the x-axis.
        y (float): Location of a given pin along the y-axis.

    Returns:
        bool: Whether the pin in question is within the given radius of the HEDGEHOG base centre.
    """

    x /= 10
    y /= 10
    pinrad = d_across_pinbase / 2
    tolerance = 1E-2

    r = np.sqrt(x**2 + y**2)
    if (r + pinrad) > (rad + tolerance):
        return False
    return True


def build(d_across_pinbase, baseEdges, filename, SOBPeak, undersim,
          tolerance, usrWeights, rad, zsep, radius_cutoff, pinData=None):
    """Main function for construction of the HEDGEHOG in GDML format."""

    if not filename:
        filename = sys.argv[1]

    reg = pyg4ometry.geant4.Registry()

    if not pinData:
        pinData = optimizer(SOBPeak, undersim, d_across_pinbase, tolerance,
                            usrWeights, radius_cutoff, filename=filename, show=1)

    print(f"creating pins... 0%", end='', flush=True)

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

    # get the original thickness just larger
    # than the largest after the slicing above
    baseIndex = np.where(pinData["thicknesses"] == thicknesses[0])[0][-1]
    baseThickness = pinData["thicknesses"][baseIndex - 1]

    # move pins down to meet the base at z=0
    thicknesses -= thicknesses[0]

    # make air box around hedgehog
    hbox_thick = thicknesses.max() + 0.5
    # move everything to the correct z location
    new_zero = zsep

    hb1 = pyg4ometry.geant4.solid.Box("hb1", 9, 9,
                                      hbox_thick, reg, lunit="cm")
    hb1_l = pyg4ometry.geant4.LogicalVolume(hb1, "G4_AIR", "hb1_l", reg,
                                            lunit="cm")
    pyg4ometry.geant4.\
        PhysicalVolume([0, 0, 0],
                       [0, 0, (new_zero + (hbox_thick/2))*10],
                       hb1_l, "hb1_p", wl, reg)

    # extra base area for attaching to mount (cm), currently 1cm
    extra = 1

    shortCoord = (baseEdges/2 - baseThickness)
    longCoord = (baseEdges/2)

    # create the base object with planes for STL conversion
    b1 = pyg4ometry.geant4.solid.GenericTrap("b1", shortCoord, longCoord,
                                             shortCoord, -longCoord,
                                             -longCoord - extra, -longCoord,
                                             -longCoord - extra, longCoord,
                                             longCoord, longCoord,
                                             longCoord, -longCoord,
                                             -longCoord - extra, -longCoord,
                                             -longCoord - extra, longCoord,
                                             baseThickness/2, reg,
                                             lunit="cm")
    b1_l = pyg4ometry.geant4.LogicalVolume(b1, "G4_Fe", "b1_l", reg,
                                           lunit="cm")
    pyg4ometry.geant4.PhysicalVolume([0, 0, 0],
                                     [0, 0, (baseThickness/2 -
                                             hbox_thick/2)*10],
                                     b1_l, "b1_p", hb1_l, reg)

    # base with no planes for FLUKA
    nb1 = pyg4ometry.geant4.solid.Box("nb1", baseEdges, baseEdges,
                                      baseThickness, reg, lunit="cm")
    nb1_l = pyg4ometry.geant4.LogicalVolume(nb1, "G4_Fe", "nb1_l", reg,
                                            lunit="cm")
    pyg4ometry.geant4.PhysicalVolume([0, 0, 0],
                                     [0, 0, (baseThickness/2 -
                                             hbox_thick/2)*10],
                                     nb1_l, "nb1_p", hb1_l, reg)

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

        xrow += 1

        # the factor of 10 is there to correct the units, there are a few
        # rogue factors of 10 around to account for this.
        for j, y in enumerate(np.round(usingArrY, 5) * 10):

            count += 1

            if circCheck(rad, d_across_pinbase, x, y):

                b2 = pyg4ometry.geant4.\
                    solid.Polycone(f"cone_s-{i}-{j}", 0, 2 * np.pi,
                                   thicknesses, np.zeros_like(pinData["radii"]),
                                   radii, reg, lunit="cm")
                b2_l = pyg4ometry.geant4.\
                    LogicalVolume(b2, "G4_Fe", f"cone_l-{i}-{j}", reg,
                                  lunit="cm")
                pyg4ometry.geant4.\
                    PhysicalVolume([0, 0, 0], [x, y, (- hbox_thick/2 +
                                                      baseThickness)*10],
                                   b2_l, f"cone_p-{i}-{j}", hb1_l, reg)

                # print(f"{np.round(count * 100 / no_pins, 1)}"
                #       f"% complete, pin at x: {x/10}, y: {y/10}")
                print('\r    \r', end='', flush=True)
                print(f"creating pins... {np.round(count * 100 / no_pins, 1)}%", end='', flush=True)

    print('\r    \r', end='', flush=True)
    print('100% complete')
    print("writing...", end='', flush=True)
    writer = pyg4ometry.gdml.Writer()
    # write to file
    writer.addDetector(reg)
    writer.write(f"{filename}.gdml")
    print('\r    \r', end='', flush=True)
    print("writing... done")

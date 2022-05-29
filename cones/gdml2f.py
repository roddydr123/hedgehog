import pyg4ometry
import sys
import re
from coneGDML import path


def convert(zsep, file=None):

    if not file:
        file = sys.argv[1]
    print("opening file...")

    reader = pyg4ometry.gdml.Reader(f"{path}files/{file}.gdml")
    world = reader.getRegistry().getWorldVolume()

    # do the conversion to fluka geometry
    print("converting...")
    freg = pyg4ometry.convert.geant4Logical2Fluka(world)

    # remove water and black hole and correctly assign materials
    # by transferring required bodies/regions to newfreg

    toDel = []

    for key in freg.regionDict:
        region = freg.regionDict[key]
        if checkRegion(key) == 0:
            toDel.append(key)
        elif key == "R0002":
            freg.assignma("AIR", region)
        else:
            freg.assignma("PMMA", region)

    for key in toDel:
        del freg.regionDict[key]

    print("writing...")
    w = pyg4ometry.fluka.Writer()
    w.addDetector(freg)
    w.write(f"{path}files/{file}.inp")
    print("adding to template...")
    addToTemplate(file, zsep)
    print("complete!")


def checkRegion(key):
    if key == "R0000":
        return 0
    elif key == "BLKHOLE":
        return 0
    else:
        return 1


def addToTemplate(filename, zsep):

    # choose the template based on z separation
    if zsep == 36.5:
        template = open("static/beamline.inp", "r")

        # template = open("static/reverse.inp", "r") for reverse hedgehog
    else:
        template = open("static/template.inp", "r")

    # merge the generated geometry with a template file
    with open(f"{path}files/{filename}geo.inp", "w") as file:
        templines = template.readlines()
        geometryfile = open(f"{path}files/{filename}.inp", "r")
        geolines = geometryfile.readlines()[:-1]
        # split the template
        for i in range(len(templines)):
            if "* Geometry gets spliced in here" in templines[i]:
                geoindex = i
            elif "* everything else spliced in here" in templines[i]:
                elseindex = i

        # split geometry file into segments
        indices = []
        for i in range(len(geolines)):
            if "END" in geolines[i]:
                indices.append(i)

        geomsplit = geolines[2:indices[0]]
        regsplit = geolines[indices[0]:indices[1]]
        assignROT = geolines[indices[2]+1:]

        # fix the parentheses problem
        geostring = "".join(regsplit)
        pp = re.compile('-\((\n* +)\+(B\w+\n*)( +-B\w+)\)')
        qq = re.compile('-\((\n* +)\+(B\w+)\)')

        new = re.sub(pp, '\\1-\\2\\3', geostring)
        regsplit = re.sub(qq, '\\1-\\2', new)

        file.writelines(templines[:geoindex])
        file.writelines(geomsplit)
        file.writelines(regsplit)
        file.writelines(templines[geoindex:elseindex])
        file.writelines(assignROT)
        file.writelines(templines[elseindex:])

        template.close()
        geometryfile.close()


if __name__ == "__main__":
    convert()

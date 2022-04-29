import pyg4ometry
import sys
import re
from coneGDML import path


def convert(zsep, file=None):

    if not file:
        file = sys.argv[1]
    print("opening file...")

    reader = pyg4ometry.gdml.Reader(f"{path}files/{file}.gdml")
    logical = reader.getRegistry().getWorldVolume()

    # do the conversion to fluka geometry
    print("converting...")
    freg = pyg4ometry.convert.geant4Logical2Fluka(logical)

    # correctly assign materials
    for key in freg.regionDict:
        region = freg.regionDict[key]
        if key == "R0000":
            freg.assignma("AIR", region)
        elif key == "BLKHOLE":
            freg.assignma("BLCKHOLE", region)
        elif key == "R0003":
            freg.assignma("WATER", region)
        else:
            freg.assignma("PMMA", region)

    print("writing...")
    w = pyg4ometry.fluka.Writer()
    w.addDetector(freg)
    w.write(f"{path}files/{file}.inp")
    print("adding to template...")
    addToTemplate(file, zsep)
    print("complete!")


def addToTemplate(filename, zsep):

    # choose the template based on z separation
    if zsep == 36.5:
        template = open("static/gtemplate36.inp", "r")
    else:
        template = open("static/template.inp", "r")

    # merge the generated geometry with a template file
    with open(f"{path}files/{filename}geo.inp", "w") as file:
        templines = template.readlines()
        geometryfile = open(f"{path}files/{filename}.inp", "r")
        geolines = geometryfile.readlines()[:-1]
        # split the template
        for i in range(len(templines)):
            if "LOW-NEUT" in templines[i]:
                splitindex = i
        before = templines[:splitindex]
        after = templines[splitindex:]

        # fix the parentheses problem
        geostring = "".join(geolines)
        pp = re.compile('-\((\n* +)\+(B\w+\n*)( +-B\w+)\)')
        qq = re.compile('-\((\n* +)\+(B\w+)\)')

        new = re.sub(pp, '\\1-\\2\\3', geostring)
        new = re.sub(qq, '\\1-\\2', new)

        file.writelines(before)
        file.writelines(new)
        file.writelines(after)

        template.close()
        geometryfile.close()


if __name__ == "__main__":
    convert()

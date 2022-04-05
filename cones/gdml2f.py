import pyg4ometry
import sys
import re


def convert(file=None):

    if not file:
        file = sys.argv[1]
    print("opening file...")

    reader = pyg4ometry.gdml.Reader(f"files/{file}.gdml")
    logical = reader.getRegistry().getWorldVolume()

    # do the conversion to fluka geometry
    print("converting...")
    freg = pyg4ometry.convert.geant4Logical2Fluka(logical)

    # correctly assign materials
    for key in freg.regionDict:
        if key == "R0000":
            freg.assignma("AIR", freg.regionDict[key])
        elif key == "BLKHOLE":
            freg.assignma("BLCKHOLE", freg.regionDict[key])
        elif key == "R0003":
            freg.assignma("WATER", freg.regionDict[key])
        else:
            freg.assignma("PMMA", freg.regionDict[key])

    print("writing...")
    w = pyg4ometry.fluka.Writer()
    w.addDetector(freg)
    w.write(f"files/{file}.inp")
    print("adding to template...")
    addToTemplate(file)
    print("complete!")


def addToTemplate(filename):
    # merge the generated geometry with a template file
    with open(f"files/{filename}geo.inp", "w") as file:
        template = open("files/template.inp", "r")
        templines = template.readlines()
        geometryfile = open(f"files/{filename}.inp", "r")
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

import sys
from coneGDML import build
from gdml2f import convert


file = sys.argv[1]
build(file)
convert(file)

Programme for optimizing, simulating and creating 3D printable HEDGEHOGs (3D range modulators for proton therapy)

Installation:
1. install pyg4ometry version 1.0.4 with "pip install pyg4ometry==1.0.4".
2. clone repo with "git clone git@github.com:roddydr123/hedgehog.git".
3. copy nist_materials.txt and nist_elements.txt into pyg4ometry package directory "pyg4ometry/geant4/".


Use runner.py as example of setting up to produce a HEDGEHOG.
Good luck!

 - For FLUKA simulation input generation, easiest to use 'template.inp' and change the geometry and settings from there.
    - alternatively look through 'template.inp' and 'gdml2f.py' for clues on the essential components.
from coneGDML import build
import gdml2f as g2f
import gdml2stl as g2s
from cubic import optimizer


class hedgehog:

    def __init__(self, SOBPeak, undersim, filename, d_across_pinbase=0.7,
                 tolerance=1E-4, usrWeights=[1, 1, 1]):
        """Object which allows running of HEDGEHOG optimizations.

        Args:
            SOBPeak (Object): Describes the shape of the desired SOBP.
            undersim (Object): Contains details of the PMMA thicknesses of the underlying simulations, and the path to the simulation data.
            filename (string): The path and filename where the HEDGEHOG outfiles will be placed.
            d_across_pinbase (float, optional): Diameter of the base of each pin. Defaults to 0.7.
            tolerance (scientific notation, optional): Tolerance of the optimization; converges to within this number. Defaults to 1E-4.
            usrWeights (list, optional): Weights to be placed on the plateau, proximal and distal edges of the SOBP. Defaults to [1, 1, 1].
        """
        self.SOBPeak = SOBPeak
        self.undersim = undersim
        self.d_across_pinbase = d_across_pinbase
        self.tolerance = tolerance
        self.usrWeights = usrWeights
        self.filename = filename

    def viewDetails(self):
        optimizer(self.SOBPeak, self.undersim, self.d_across_pinbase, self.tolerance,
                  self.usrWeights, show=1, filename=self.filename)

    def generateGDML(self, baseEdges, rad, zsep):
        """Runs an optimisation sequence and builds the geometry in GDML format.

        Args:
            baseEdges (float): Length of the edges of the HEDGEHOG base in cm.
            rad (float): Radius from centre of base to build pins in. Usually set to half the shortest baseEdge.
            zsep (float): Distance between upstream edge of water target and point where HEDGEHOG pins meet its base.
        """

        self.baseEdges = baseEdges
        self.rad = rad
        self.zsep = zsep
        build(self.d_across_pinbase, self.baseEdges, self.filename, self.SOBPeak,
              self.undersim, self.tolerance, self.usrWeights, self.rad, self.zsep)

    def gdml2f(self, template):
        g2f.convert(template, filename=self.filename)

    def gdml2stl(self):
        g2s.convert(filename=self.filename)


class undersim:

    def __init__(self, thicklist, filepath):
        self.thicklist = thicklist
        self.filepath = filepath


class SOBPeak:

    def __init__(self, SOBPwidth, range, steps):
        self.width = SOBPwidth
        self.range = range
        self.steps = steps

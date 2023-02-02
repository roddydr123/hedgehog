from coneGDML import build
import gdml2f as g2f
import gdml2stl as g2s
from cubic import optimizer


class hedgehog:
    """Object which allows running of HEDGEHOG optimizations.
    """

    def __init__(self, SOBPeak, undersim, filename, d_across_pinbase=0.7,
                 tolerance=1E-4, usrWeights=[1, 1, 1], radius_cutoff=0.02):
        """Initialise a HEDGEHOG instance.

        Args:
            SOBPeak (Object): Describes the shape of the desired SOBP.
            undersim (Object): Contains details of the PMMA thicknesses of the underlying simulations, and the path to the simulation data.
            filename (string): The path and filename where the HEDGEHOG outfiles will be placed.
            d_across_pinbase (float, optional): Diameter of the base of each pin. Defaults to 0.7.
            tolerance (scientific notation, optional): Tolerance of the optimization; converges to within this number. Defaults to 1E-4.
            usrWeights (list, optional): Weights to be placed on the plateau, proximal and distal edges of the SOBP. Defaults to [1, 1, 1].
            radius_cutoff (float, optional): Used to cut off the tips of pins if they are produced with very thin tips which will not print properly.
        """
        self.SOBPeak = SOBPeak
        self.undersim = undersim
        self.d_across_pinbase = d_across_pinbase
        self.tolerance = tolerance
        self.usrWeights = usrWeights
        self.filename = filename
        self.radius_cutoff = radius_cutoff

    def viewDetails(self):
        """Run an optimization but without making a geometry file or saving details.
        """
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
              self.undersim, self.tolerance, self.usrWeights, self.rad, self.zsep, self.radius_cutoff)

    def gdml2f(self, template):
        g2f.convert(template, filename=self.filename)

    def gdml2stl(self):
        g2s.convert(filename=self.filename)


class undersim:
    """Object to contain details of underlying FLUKA simulations for an optimization.
    """

    def __init__(self, thicklist, filepath):
        """Initialise class.

        Args:
            thicklist (list): Contains the thicknesses of HEDGEHOG material in the underlying simulations.
            filepath (str): Location of the directory of the underlying simulations.
        """
        self.thicklist = thicklist
        self.filepath = filepath


class SOBPeak:
    """Object to contain details of the desired SOBP.
    """

    def __init__(self, SOBPwidth, range, steps):
        """Initialise class.

        Args:
            SOBPwidth (float): Desired axial spread of dose, i.e. the width of the plateau.
            range (float): Desired depth of distal edge of SOBP plateau.
            steps (int): Number of spline points to use in the optimisation. Good idea to play around with this number
            as problems (such as oscillations in weights) can occur.
        """
        self.width = SOBPwidth
        self.range = range
        self.steps = steps

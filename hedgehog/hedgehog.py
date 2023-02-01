from coneGDML import build
import gdml2f as g2f
import gdml2stl as g2s
from cubic import optimizer


class hedgehog:

    def __init__(self, SOBPeak, undersim, filename, d_across_pinbase=0.7,
                 tolerance=1E-4, usrWeights=[1, 1, 1]):
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
        # zsep is location of hedgehog in geometry
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

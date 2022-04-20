from coneGDML import build
import gdml2f as g2f
import gdml2stl as g2s
from cubic import optimizer


class hedgehog():

    def __init__(self, SOBPwidth, range, steps, d_across_pinbase, tolerance,
                 filename=None):
        self.SOBPwidth = SOBPwidth
        self.range = range
        self.steps = steps
        self.d_across_pinbase = d_across_pinbase
        self.tolerance = tolerance
        self.pinData = None
        self.filename = filename

    def viewDetails(self):
        self.pinData = optimizer(self.SOBPwidth, self.range, self.steps,
                                 self.d_across_pinbase, self.tolerance,
                                 show=1, filename=self.filename)

    def generateGDML(self, baseEdges):
        self.baseEdges = baseEdges
        build(self.d_across_pinbase, self.baseEdges, self.filename,
              self.SOBPwidth, self.range, self.steps, self.tolerance,
              pinData=self.pinData)

    def gdml2f(self):
        g2f.convert(file=self.filename)

    def gdml2stl(self):
        g2s.convert(filename=self.filename)

    def toFLUKA(self):
        self.generateGDML()
        self.gdml2f()

    def toSTL(self):
        self.generateGDML()
        self.gdml2stl()

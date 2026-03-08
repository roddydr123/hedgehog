import pathlib

import hedgehog.gdml2f as g2f
import hedgehog.gdml2stl as g2s
from hedgehog.coneGDML import build
from hedgehog.cubic import optimizer
from hedgehog.static_classes import SOBPeak_cls, Undersim


class hedgehog:
    """Object which allows running of HEDGEHOG optimizations."""

    def __init__(
        self,
        SOBPeak: SOBPeak_cls,
        undersim: Undersim,
        filename: str | pathlib.Path,
        d_across_pinbase: float = 0.7,
        tolerance: float = 1e-4,
        usrWeights: tuple[float, float, float] = (1, 1, 1),
        radius_cutoff: float = 0.02,
    ):
        """Initialise a HEDGEHOG instance.

        Args:
            SOBPeak (Object): Describes the shape of the desired SOBP.
            undersim (Object): Contains details of the PMMA thicknesses of the
                underlying simulations, and the path to the simulation data.
            filename (string): The path and filename where the HEDGEHOG
                outfiles will be placed.
            d_across_pinbase (float, optional): Diameter of the base of
                each pin. Defaults to 0.7.
            tolerance (scientific notation, optional): Tolerance of
                the optimization; converges to within this number. Defaults
                to 1E-4.
            usrWeights (tuple, optional): Weights to be placed on the plateau,
                proximal and distal edges of the SOBP. Defaults to (1, 1, 1).
            radius_cutoff (float, optional): Used to cut off the tips of
                pins if they are produced with very thin tips which will not
                print properly.
        """
        self.SOBPeak = SOBPeak
        self.undersim = undersim
        self.d_across_pinbase = d_across_pinbase
        self.tolerance = tolerance
        self.usrWeights = usrWeights
        self.filename = filename
        self.radius_cutoff = radius_cutoff

    def viewDetails(self) -> None:
        """Run an optimization but without making a geometry file or saving details."""
        optimizer(
            self.SOBPeak,
            self.undersim,
            self.d_across_pinbase,
            self.tolerance,
            self.usrWeights,
            self.radius_cutoff,
            show=True,
            filename=self.filename,
        )

    def generateGDML(self, baseEdges: float, rad: float, zsep: float) -> None:
        """Runs an optimisation sequence and builds the geometry in GDML format.

        Args:
            baseEdges (float): Length of the edges of the HEDGEHOG base in cm.
            rad (float): Radius from centre of base to build pins in. Usually set to half the shortest baseEdge.
            zsep (float): Distance between upstream edge of water target and point where HEDGEHOG pins meet its base.
        """

        self.baseEdges = baseEdges
        self.rad = rad
        self.zsep = zsep
        build(
            self.d_across_pinbase,
            self.baseEdges,
            self.filename,
            self.SOBPeak,
            self.undersim,
            self.tolerance,
            self.usrWeights,
            self.rad,
            self.zsep,
            self.radius_cutoff,
        )

    def gdml2f(self, template: str | pathlib.Path) -> None:
        g2f.convert(template, filename=self.filename)

    def gdml2stl(self) -> None:
        g2s.convert(filename=self.filename)

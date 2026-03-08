import pathlib


class Undersim:
    """Object to contain details of underlying FLUKA simulations for an optimization."""

    def __init__(self, thicklist: list, filepath: str | pathlib.Path) -> None:
        """Initialise class.

        Args:
            thicklist (list): Contains the thicknesses of HEDGEHOG material in the underlying simulations.
            filepath (str | pathlib.Path): Location of the directory of the underlying simulations.
        """
        self.thicklist = thicklist
        self.filepath = filepath


class SOBPeak_cls:
    """Object to contain details of the desired SOBP."""

    def __init__(self, SOBPwidth: float, range: float, steps: int) -> None:
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

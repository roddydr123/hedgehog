import hedgehog.classes as hog
import pathlib


RUN_PATH = pathlib.Path(__file__)


def test_it_runs(tmp_path):
    # PMMA thicknesses of underlying simulations.
    thicklist = [0.1, 0.19, 0.29, 0.38, 0.47, 0.57, 0.66, 0.75, 0.85, 0.94, 1.03,
                 1.13, 1.22, 1.31, 1.41, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2,
                 2.3, 2.4, 2.5, 2.6, 2.7, 2.8]

    # provide path to underlying sims.
    sim_path = RUN_PATH.parents[1] / "hedgehog" / "usims"
    us = hog.undersim(thicklist, sim_path)

    # provide desired SOBP details.
    sobp = hog.SOBPeak(2.5, 4.0, 10)

    # create hedgehog instance with location to store produced files and convergence point of optimization.
    h = hog.hedgehog(sobp, us, tmp_path.joinpath("test_output"), tolerance=1E-3)

    # uncomment to perform optimization but do not create geometry.
    # h.viewDetails()

    # run optimization and create a HEDGEHOG geometry.
    h.generateGDML(5, 1.5, 13.6)

    # convert the GDML file into a FLUKA input file with the given template.
    h.gdml2f(RUN_PATH.parents[1] / "hedgehog" / "template.inp")

    # convert the GDML file into an STL file for 3D printing.
    h.gdml2stl()

    assert tmp_path.joinpath("test_output.gdml").exists()
    assert tmp_path.joinpath("test_output.inp").exists()
    assert tmp_path.joinpath("test_output.stl").exists()

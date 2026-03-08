import pathlib
import pickle
import shutil

import numpy as np

import hedgehog.classes as hog
import hedgehog.static_classes as stat_hog
from hedgehog.cubic import optimizer
from tests.test_utils import files_equal_to_ndp, stl_same_geometry, util_test_files_identical_line_by_line


RUN_PATH = pathlib.Path(__file__)


def test_it_runs(tmp_path: pathlib.Path) -> None:
    # PMMA thicknesses of underlying simulations.
    thicklist = [
        0.1,
        0.19,
        0.29,
        0.38,
        0.47,
        0.57,
        0.66,
        0.75,
        0.85,
        0.94,
        1.03,
        1.13,
        1.22,
        1.31,
        1.41,
        1.5,
        1.6,
        1.7,
        1.8,
        1.9,
        2.0,
        2.1,
        2.2,
        2.3,
        2.4,
        2.5,
        2.6,
        2.7,
        2.8,
    ]

    # provide path to underlying sims.
    sim_path = RUN_PATH.parents[1] / "hedgehog" / "usims"
    us = stat_hog.Undersim(thicklist, sim_path)

    # provide desired SOBP details.
    sobp = stat_hog.SOBPeak_cls(2.5, 4.0, 10)

    # create hedgehog instance with location to store produced files and convergence point of optimization.
    h = hog.hedgehog(sobp, us, tmp_path.joinpath("test_output"), tolerance=1e-3)

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

    files_equal_to_ndp(tmp_path.joinpath("test_output.gdml"), RUN_PATH.parent / "test_data" / "test_output.gdml")
    files_equal_to_ndp(tmp_path.joinpath("test_output.inp"), RUN_PATH.parent / "test_data" / "test_output.inp")


def test_gdml2f(tmp_path: pathlib.Path) -> None:
    """Only test gdml to fluka conversion"""

    thicklist = [
        0.1,
        0.19,
        0.29,
        0.38,
        0.47,
        0.57,
        0.66,
        0.75,
        0.85,
        0.94,
        1.03,
        1.13,
        1.22,
        1.31,
        1.41,
        1.5,
        1.6,
        1.7,
        1.8,
        1.9,
        2.0,
        2.1,
        2.2,
        2.3,
        2.4,
        2.5,
        2.6,
        2.7,
        2.8,
    ]

    # provide path to underlying sims.
    sim_path = RUN_PATH.parents[1] / "hedgehog" / "usims"
    us = stat_hog.Undersim(thicklist, sim_path)

    # provide desired SOBP details.
    sobp = stat_hog.SOBPeak_cls(2.5, 4.0, 10)

    # create hedgehog instance with location to store produced files and convergence point of optimization.
    h = hog.hedgehog(sobp, us, tmp_path.joinpath("test_output"), tolerance=1e-3)

    # copy the gdml ready for conversion
    shutil.copy(RUN_PATH.parent / "test_data" / "test_output.gdml", tmp_path.joinpath("test_output.gdml"))

    h.gdml2f(RUN_PATH.parents[1] / "hedgehog" / "template.inp")

    assert tmp_path.joinpath("test_output.inp").exists()

    util_test_files_identical_line_by_line(
        tmp_path.joinpath("test_output.inp"), RUN_PATH.parent / "test_data" / "test_output.inp"
    )


def test_gdml2stl(tmp_path: pathlib.Path) -> None:

    thicklist = [
        0.1,
        0.19,
        0.29,
        0.38,
        0.47,
        0.57,
        0.66,
        0.75,
        0.85,
        0.94,
        1.03,
        1.13,
        1.22,
        1.31,
        1.41,
        1.5,
        1.6,
        1.7,
        1.8,
        1.9,
        2.0,
        2.1,
        2.2,
        2.3,
        2.4,
        2.5,
        2.6,
        2.7,
        2.8,
    ]

    # provide path to underlying sims.
    sim_path = RUN_PATH.parents[1] / "hedgehog" / "usims"
    us = stat_hog.Undersim(thicklist, sim_path)

    # provide desired SOBP details.
    sobp = stat_hog.SOBPeak_cls(2.5, 4.0, 10)

    # create hedgehog instance with location to store produced files and convergence point of optimization.
    h = hog.hedgehog(sobp, us, tmp_path.joinpath("test_output"), tolerance=1e-3)

    # copy the gdml ready for conversion
    shutil.copy(RUN_PATH.parent / "test_data" / "test_output.gdml", tmp_path.joinpath("test_output.gdml"))

    h.gdml2stl()

    assert tmp_path.joinpath("test_output.stl").exists()

    stl_same_geometry(tmp_path.joinpath("test_output.stl"), RUN_PATH.parent / "test_data" / "test_output.stl")


def test_optimizer(tmp_path: pathlib.Path) -> None:

    thicklist = [
        0.1,
        0.19,
        0.29,
        0.38,
        0.47,
        0.57,
        0.66,
        0.75,
        0.85,
        0.94,
        1.03,
        1.13,
        1.22,
        1.31,
        1.41,
        1.5,
        1.6,
        1.7,
        1.8,
        1.9,
        2.0,
        2.1,
        2.2,
        2.3,
        2.4,
        2.5,
        2.6,
        2.7,
        2.8,
    ]

    # provide path to underlying sims.
    sim_path = RUN_PATH.parents[1] / "hedgehog" / "usims"
    us = stat_hog.Undersim(thicklist, sim_path)

    # provide desired SOBP details.
    sobp = stat_hog.SOBPeak_cls(2.5, 4.0, 10)

    # create hedgehog instance with location to store produced files and convergence point of optimization.
    h = hog.hedgehog(sobp, us, tmp_path.joinpath("test_output"), tolerance=1e-3)

    pinData = optimizer(
        h.SOBPeak,
        h.undersim,
        h.d_across_pinbase,
        h.tolerance,
        h.usrWeights,
        h.radius_cutoff,
        filename=h.filename,
        show=False,
    )

    with open(RUN_PATH.parent / "test_data" / "pinData.pkl", "rb") as f:
        exp_pinData = pickle.load(f)

    assert np.all(np.isclose(pinData["radii"], exp_pinData["radii"]))
    assert np.all(np.isclose(pinData["thicknesses"], exp_pinData["thicknesses"]))

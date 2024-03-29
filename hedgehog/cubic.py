import scipy.interpolate as interpolate
import scipy.optimize as opt
import os
import numpy as np
import matplotlib.pyplot as plt
import weightsCone as wc
from SOBPwidth import getwidth
import re


def logger(data, first=False):
    if first is True:
        with open("optimiser.log", "w") as file:
            file.write(f"{data}\n")
    else:
        with open("optimiser.log", "a") as file:
            file.write(f"{data}\n")


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def getSimData(undersim):
    doses = []
    peaks = []

    for root, dirs, files in os.walk(undersim.filepath, topdown=True):
        files.sort(key=natural_keys)
        for file in files:
            data = np.genfromtxt(f"{undersim.filepath}/{file}", skip_header=1)
            dose = data[:, 2]
            # make depth start at zero
            depth = data[:, 0] - data[0, 0]
            doses.append(dose)
            # store the depth of each peak
            peaks.append(depth[dose.argmax()])

    doses = np.array(doses)

    # normalise all the BPs relative to the highest peak
    #doses = doses / doses.max()

    simDataDict = {"thicknesses": undersim.thicklist, "depth": depth, "doses": doses,
                   "peaks": peaks}

    return simDataDict


def genInitGuess(SOBPeak, d_across_pinbase, peaks=None, thicknesses=None):
    """
    Finds an initial guess stepped hedgehog in terms of
    the thickness vs weight of PMMA using weightsCone.py.
    """

    height, weights, desired = wc.blockSpecs(SOBPeak)
    # finding the base thickness as the thickness which will
    # results in a peak at the range point
    peak_interp = interpolate.UnivariateSpline(peaks[::-1],
                                               thicknesses[::-1], s=0,
                                               ext=1)
    base_thickness = peak_interp(desired[0])
    if base_thickness == 0.0:
        raise ValueError("Your desired SOBP is outwith the range of the \
                         underlying simulations. Please reduce the range.")
    """
    leading = base_thickness // height

    # add zero weight thicknesses either end of the pin for opt to play with
    padding_zeros = int(leading)
    base_thickness -= (padding_zeros * height)
    extra_weights = [0.0] * padding_zeros
    weights = np.append(weights, extra_weights)
    weights = np.insert(weights, 0, extra_weights)
    """
    # find the thicknesses from the heights
    new_thicknesses = np.zeros_like(weights)

    for i, thick in enumerate(new_thicknesses):
        # bottom -> top as we build the pins
        # add the base thickness
        new_thicknesses[i] = (i * height) + base_thickness

    return new_thicknesses, weights, desired, base_thickness


def genSOBP(thicknesses, weights, sDDict, d_across_pinbase, radius_cutoff, show=0,
            desired=None, filename=None, base_thickness=None):
    """
    Takes a thickness profile and generates an SOBP from it
    using the interpolated matrix.
    """
    # make the full thickness profile W(T)
    density = 100
    dense_thicknesses = np.linspace(thicknesses[0], thicknesses[-1], density)
    interp_weights = interpolate.UnivariateSpline(thicknesses, weights, s=0)
    dense_weights = interp_weights(dense_thicknesses)

    # set any negative weights to zero as they're unphysical
    dense_weights = np.where(dense_weights > 0, dense_weights, 0)

    # set any weights for thicknesses less than the base to zero
    dense_weights = np.where(dense_thicknesses > base_thickness,
                             dense_weights, 0)
    """
    # set any weights after the first zero to zero, as an artefact of cubic
    # splines can make extra bumps in the weights profile. Cut in half to
    # not include leading zeros.
    half = dense_weights[int(len(dense_weights) / 2):][::-1]
    try:
        zero_index = np.where(half == 0)[0][-1] + 1
        dense_weights[-zero_index:] = 0
    except IndexError:
        # sometimes there are no zeros...
        pass
    """

    # now find the depth-dose profile (BP) for each thickness by interpolation
    # we don't interpolate along the depth-dose profile at the moment, could
    # change that
    interp_dose = interpolate.RectBivariateSpline(sDDict["thicknesses"],
                                                  sDDict["depth"],
                                                  sDDict["doses"], s=0)
    dense_doses = interp_dose(dense_thicknesses, sDDict["depth"])

    # calculate radii from the full pin profile and return it for
    # building the pins in gdml
    radii = wc.wToRadii(dense_weights, d_across_pinbase)

    # trim small radii
    slice = radii > radius_cutoff
    radii = radii[slice]
    dense_thicknesses = dense_thicknesses[slice]
    dense_weights = dense_weights[slice]
    dense_doses = dense_doses[slice]

    # perform a weighted sum of the BPs
    sobp = np.dot(dense_doses.T, dense_weights)

    # and normalise again :)
    sobp = sobp / sobp.max()

    depth_dose_sobp = [sDDict["depth"], sobp]

    if show:
        # print SOBP data
        getwidth(depth_dose_sobp[0], depth_dose_sobp[1])

        fig = plt.figure()

        # show a plot of the final SOBP
        ax1 = fig.add_subplot(222)
        ax1.scatter(depth_dose_sobp[0], depth_dose_sobp[1], s=2)
        ymax = depth_dose_sobp[1].max()
        ax1.vlines(desired[0] - desired[1], 0, ymax)
        ax1.vlines(desired[0], 0, ymax)
        ax1.set_xlabel("Depth (cm)")
        ax1.set_ylabel("Dose")

        # show a plot of the thickness profile of the pin in terms of radii
        ax2 = fig.add_subplot(223)
        ax2.plot(radii, dense_thicknesses)
        ax2.set_ylabel("Pin thickness (cm)")
        ax2.set_xlabel("Pin radius (cm)")

        # show a plot of the weights profile
        ax3 = fig.add_subplot(224)
        ax3.scatter(thicknesses[:-2], weights[:-2], s=7, color='k')
        ax3.plot(dense_thicknesses, dense_weights)
        ax3.set_xlabel("Thickness (cm)")
        ax3.set_ylabel("Weight")

        # plot the constituent BPs
        ax4 = fig.add_subplot(221)
        wdose = []
        for i, dose in enumerate(dense_doses):
            ax4.plot(depth_dose_sobp[0], dose * dense_weights[i])
            wdose.append(dose * dense_weights[i])
        ax4.plot(depth_dose_sobp[0], np.sum(wdose, axis=0))
        ax4.set_xlabel("Depth (cm)")
        ax4.set_ylabel("Dose")

        if filename:
            np.savez(f'{filename}', depth_dose_sobp=depth_dose_sobp)

        plt.show()

    pinData = {"radii": radii, "thicknesses": dense_thicknesses}

    return depth_dose_sobp, pinData


def objectiveFunc(weights, thicknesses, desired, sDDict, d_across_pinbase,
                  usrWeights, base_thickness, radius_cutoff):

    range = desired[0]
    plat_width = desired[1]

    # get the sobp for this thickness profile and
    # partition it into entrance, target and exit regions
    depth_dose_sobp, pinData = \
        genSOBP(thicknesses, weights, sDDict, d_across_pinbase, radius_cutoff,
                desired=desired, base_thickness=base_thickness)
    # the slices are truth arrays
    ent_region_slice = depth_dose_sobp[0] < (range - plat_width)
    exit_region_slice = depth_dose_sobp[0] > range
    target_region_slice = (depth_dose_sobp[0] <= range) &\
                          (depth_dose_sobp[0] >= range - plat_width)
    ent_dose = depth_dose_sobp[1][ent_region_slice]
    exit_dose = depth_dose_sobp[1][exit_region_slice]
    target_dose = depth_dose_sobp[1][target_region_slice]

    # find the entrance and exit dose sums
    ent_sum = np.sum(ent_dose)
    exit_sum = np.sum(exit_dose)

    # and the standard deviation of the target region
    target_stdev = np.std(target_dose)

    # new opt-weights
    optWeights = np.array([usrWeights[0] / 0.02, usrWeights[1] / len(ent_dose),
                          usrWeights[2] / len(exit_dose)])

    # finally calculate the objective function value
    scalar = (optWeights[0] * target_stdev) + (optWeights[1] * ent_sum) +\
             (optWeights[2] * exit_sum)

    logger(f"{scalar}  {np.round((target_stdev * 100) / np.average(target_dose),3)}")
    print('\r    \r', end='', flush=True)
    print(f"minimising... {np.round(scalar, 3)}", end='', flush=True)

    return scalar


def optimizer(SOBPeak, undersim, d_across_pinbase, tolerance, usrWeights, radius_cutoff,
              filename=None, show=1):
    """
    Calls the optimization function - objectiveFunc().
    Returns the best pin thickness profile found.
    """

    sDDict = getSimData(undersim)

    # get the details of the initial guess stepped hedgehog
    # and the weights of the SOBPs
    init_thicknesses, init_weights, desired, base_thickness = \
        genInitGuess(SOBPeak, d_across_pinbase, peaks=sDDict["peaks"],
                     thicknesses=sDDict["thicknesses"])

    x0 = init_weights
    args = (init_thicknesses, desired, sDDict, d_across_pinbase, usrWeights,
            base_thickness, radius_cutoff)

    bounds = [(0, 1)] * len(init_weights)

    options = {"maxiter": 1000}

    res = opt.minimize(objectiveFunc, x0, args=args, bounds=bounds,
                       method="SLSQP", tol=tolerance, options=options)
    print(f"\n\n{res.message}\n\n")
    logger("\n\nEND OF OPTIMIZATION\n")
    logger(res)
    opt_weights = res.x
    depth_dose_sobp, pinData = genSOBP(init_thicknesses, opt_weights, sDDict,
                                       d_across_pinbase, radius_cutoff, show=show,
                                       desired=desired, filename=filename,
                                       base_thickness=base_thickness)

    return pinData


if __name__ == "__main__":
    optimizer()

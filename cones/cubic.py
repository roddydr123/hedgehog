import scipy.interpolate as interpolate
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
import weightsCone as wc
from SOBPwidth import getwidth
from weightsCone import path

waterEquiv = 1.158


def getSimData(zsep):
    doses = []
    peaks = []

    if zsep == 15:
        settings = [zsep, "using dataset 2", 17, "long", [0.1, 0.19, 0.29,
                    0.38, 0.47, 0.57, 0.66, 0.75, 0.85, 0.94, 1.03, 1.13,
                    1.22, 1.31, 1.41, 1.5]]
    elif zsep == 36.5:
        settings = [zsep, "using dataset 3", 17, "expt", [0.1, 0.19, 0.29,
                    0.38, 0.47, 0.57, 0.66, 0.75, 0.85, 0.94, 1.03, 1.13,
                    1.22, 1.31, 1.41, 1.5]]
        #settings = [zsep, "using dataset 4", 22, "fullblock", [0.1, 0.19, 0.29,
        #            0.38, 0.47, 0.57, 0.66, 0.75, 0.85, 0.94, 1.03, 1.13,
        #            1.22, 1.31, 1.41, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]]
    else:
        settings = [zsep, "using dataset 1", 22, "data", [0.05, 0.13, 0.2,
                    0.27, 0.3, 0.33, 0.4, 0.47, 0.53, 0.6, 0.67, 0.73, 0.8,
                    0.87, 0.93, 1, 1.1, 1.2, 1.3, 1.4, 1.5]]

    print(settings[1])
    # load in all the data and store the SOBP
    for i in range(1, settings[2]):
        number = format(i, "02")
        data = np.genfromtxt(f'matrix/{settings[3]}{number}.txt',
                             skip_header=1)
        dose = data[:, 2]
        depth = data[:, 0] - zsep
        doses.append(dose)
        # store the depth of each peak
        peaks.append(depth[dose.argmax()])
        thicknesses = settings[4]

    doses = np.array(doses)

    # normalise all the BPs relative to the highest peak
    doses = doses / doses.max()

    simDataDict = {"thicknesses": thicknesses, "depth": depth, "doses": doses,
                   "peaks": peaks}

    return simDataDict


def genInitGuess(SOBPwidth, range, steps, d_across_pinbase, peaks=None,
                 thicknesses=None):
    """
    Finds an initial guess stepped hedgehog in terms of
    the thickness vs weight of PMMA using weightsCone.py.
    """

    height, weights, desired = wc.blockSpecs(SOBPwidth, range, steps)

    # finding the base thickness as the thickness which will
    # results in a peak at the range point
    peak_interp = interpolate.UnivariateSpline(peaks[::-1],
                                               thicknesses[::-1], s=0)
    base_thickness = peak_interp(desired[0])

    # add zero weight thicknesses either end of the pin for opt to play with
    padding_zeros = 2
    base_thickness -= (padding_zeros * height)
    extra_weights = [0.0] * padding_zeros
    weights = np.append(weights, extra_weights)
    weights = np.insert(weights, 0, extra_weights)

    # find the thicknesses from the heights
    thicknesses = np.zeros_like(weights)
    for i, thick in enumerate(thicknesses):
        # bottom -> top as we build the pins
        # add the base thickness
        thicknesses[i] = (i * height) + base_thickness

    return thicknesses, weights, desired


def genSOBP(thicknesses, weights, sDDict, d_across_pinbase, show=0,
            desired=None, filename=None):
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
    slice = radii > 0.002
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
        ax2.scatter(radii, dense_thicknesses, s=1)
        ax2.set_ylabel("Pin thickness (cm)")
        ax2.set_xlabel("Pin radius (cm)")

        # show a plot of the weights profile
        ax3 = fig.add_subplot(224)
        ax3.plot(dense_thicknesses, dense_weights)
        ax3.scatter(thicknesses, weights)
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
            np.savez(f'{path}data/{filename}-gen',
                     depth_dose_sobp=depth_dose_sobp)

        plt.show()

    pinData = {"radii": radii, "thicknesses": dense_thicknesses}

    return depth_dose_sobp, pinData


def objectiveFunc(weights, thicknesses, desired, sDDict, d_across_pinbase,
                  usrWeights):

    range = desired[0]
    plat_width = desired[1]

    # get the sobp for this thickness profile and
    # partition it into entrance, target and exit regions
    depth_dose_sobp, pinData = \
        genSOBP(thicknesses, weights, sDDict, d_across_pinbase,
                desired=desired)
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

    print(scalar,
          f"{np.round((target_stdev * 100) / np.average(target_dose),3)}%")

    return scalar


def optimizer(SOBPwidth, range, steps, d_across_pinbase, tolerance, zsep,
              usrWeights, filename=None, show=1):
    """
    Calls the optimization function - objectiveFunc().
    Returns the best pin thickness profile found.
    """

    sDDict = getSimData(zsep)
    # get the details of the initial guess stepped hedgehog
    # and the weights of the SOBPs
    init_thicknesses, init_weights, desired = \
        genInitGuess(SOBPwidth, range, steps, d_across_pinbase,
                     peaks=sDDict["peaks"], thicknesses=sDDict["thicknesses"])

    x0 = init_weights
    args = (init_thicknesses, desired, sDDict, d_across_pinbase, usrWeights)

    bounds = [(0, 1)] * len(init_weights)

    options = {"maxiter": 1000}

    res = opt.minimize(objectiveFunc, x0, args=args, bounds=bounds,
                       method="SLSQP", tol=tolerance, options=options)
    print(res)
    opt_weights = res.x
    depth_dose_sobp, pinData = genSOBP(init_thicknesses, opt_weights, sDDict,
                                       d_across_pinbase, show=show,
                                       desired=desired, filename=filename)

    return pinData


if __name__ == "__main__":
    optimizer()

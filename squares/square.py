import scipy.interpolate as interpolate
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
import weightsSquare as ws
from SOBPwidth import getwidth


def getSimData():
    doses = []
    peaks = []
    # load in all the data and store the SOBP
    for i in range(1, 22):
        number = format(i, "02")
        data = np.genfromtxt(f'matrix/data{number}a.txt', skip_header=1)
        dose = data[:,2]
        depth = data[:,0] - 1
    
        doses.append(dose)
        # store the depth of each peak
        peaks.append(depth[dose.argmax()])
    doses = np.array(doses)

    # normalise all the BPs relative to the highest peak
    doses = doses / doses.max()

    # these are the thicknesses of pmma I simulated
    # the depth needs to have -1 because the water starts at z=1cm
    thicknesses = [0.05, 0.13, 0.2, 0.27, 0.3, 0.33, 0.4, 0.47, 0.53, 0.6, 0.67, 0.73, 0.8, 0.87, 0.93, 1, 1.1, 1.2, 1.3, 1.4, 1.5]

    simDataDict = {"thicknesses": thicknesses, "depth": depth, "doses": doses, "peaks": peaks}

    return simDataDict


def genInitGuess(peaks=None, thicknesses=None):
    """ 
    Finds an initial guess stepped hedgehog in terms of 
    the thickness vs weight of PMMA using weightsCone.py.
    """

    height, weights, desired = ws.blockSpecs()

    # finding the base thickness as the thickness which will
    # results in a peak at the range point
    peak_interp = interpolate.UnivariateSpline(peaks[::-1], thicknesses[::-1], s=0)
    base_thickness = peak_interp(desired[0]) - 0.3

    extra_weights = [0.0] * 20
    weights = np.insert(weights, -1, extra_weights)

    # find the thicknesses from the heights
    thicknesses = np.zeros_like(weights)
    for i in range(len(thicknesses)):
        # bottom -> top as we build the pins
        # add the base thickness
        thicknesses[i] = (i * height) + base_thickness
    # at the moment use the points generated from blockspecs() as the spline points
    # could change this later with an interpolation.

    # at this point, W(T) looks like a decreasing exponential from (base_thickness, weight=1)
    return thicknesses, weights, desired


def genSOBP(thicknesses, weights, sDDict, show=0, desired=None, filename=None):
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
    # we don't interpolate along the depth-dose profile at the moment, could change that
    interp_dose = interpolate.RectBivariateSpline(sDDict["thicknesses"], sDDict["depth"], sDDict["doses"], s=0)
    dense_doses = interp_dose(dense_thicknesses, sDDict["depth"])

    # renormalise the interpolated BPs
    #max_array = np.tile(np.amax(dense_doses, axis=1), [len(sDDict["depth"]), 1]).T
    #dense_doses = dense_doses / max_array

    # perform a weighted sum of the BPs
    sobp = np.dot(dense_doses.T, dense_weights)

    # and normalise again :)
    sobp = sobp / sobp.max()

    depth_dose_sobp = [sDDict["depth"], sobp]

    # calculate radii from the full pin profile and return it for
    # building the pins in gdml
    edges = ws.wToEdges(dense_weights)
    pinData = {"edges": edges, "thicknesses": dense_thicknesses}

    # set the first edge equal to the second one as the base is taken care
    # of separately
    #edges[0] = edges[1]

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
        #ax2 = fig.add_subplot(223)
        #ax2.plot(radii, dense_thicknesses)
        #ax2.set_ylabel("Pin thickness (cm)")
        #ax2.set_xlabel("Pin radius (cm)")

        # show a plot of the weights profile
        ax3 = fig.add_subplot(224)
        ax3.plot(dense_thicknesses, dense_weights)
        ax3.scatter(thicknesses, weights)
        ax3.set_xlabel("Thickness (cm)")
        ax3.set_ylabel("Weight")

        # plot of component BPs and SOBP
        ax4 = fig.add_subplot(221)
        wdose = []
        for i, dose in enumerate(dense_doses):
            ax4.plot(depth_dose_sobp[0], dose * dense_weights[i])
            wdose.append(dose * dense_weights[i])
        ax4.plot(depth_dose_sobp[0], np.sum(wdose, axis=0))
        ax4.set_xlabel("Depth (cm)")
        ax4.set_ylabel("Dose")

        if filename:
            np.savez(f'data/{filename}-gen', depth_dose_sobp=depth_dose_sobp)

        plt.show()
        """
        # make a colour plot of the dose
        fig1 = plt.figure()
        ax1 = fig1.add_subplot()
        image = ax1.imshow(dense_doses, cmap='magma',
                        origin="lower", extent=[sDDict["depth"][0], sDDict["depth"][-1], dense_thicknesses[0], dense_thicknesses[-1]],
                        interpolation='none', aspect='equal')
        plt.colorbar(image)
        plt.show()
        """
    return depth_dose_sobp, pinData


def objectiveFunc(weights, thicknesses, desired, sDDict):

    range = desired[0]
    plat_width = desired[1]

    # get the sobp for this thickness profile and
    # partition it into entrance, target and exit regions
    depth_dose_sobp, pinData = genSOBP(thicknesses, weights, sDDict, desired=desired)
    # the slices are truth arrays
    ent_region_slice = depth_dose_sobp[0] < (range - plat_width)
    exit_region_slice = depth_dose_sobp[0] > range
    target_region_slice = (depth_dose_sobp[0] <= range) & (depth_dose_sobp[0] >= range - plat_width)
    ent_dose = depth_dose_sobp[1][ent_region_slice]
    exit_dose = depth_dose_sobp[1][exit_region_slice]
    target_dose = depth_dose_sobp[1][target_region_slice]

    # find the entrance and exit dose sums
    ent_sum = np.sum(ent_dose)
    exit_sum = np.sum(exit_dose)

    # and the standard deviation of the target region
    target_stdev = np.std(target_dose)

    # new opt-weights
    usrWeights = [300, 15E2, 15E2]
    optWeights = np.array([usrWeights[0] / 0.02, usrWeights[1] / len(ent_dose), usrWeights[2] / len(exit_dose)])

    # finally calculate the objective function value
    scalar = (optWeights[0] * target_stdev) + (optWeights[1] * ent_sum) + (optWeights[2] * exit_sum)

    print(scalar, f"{np.round((target_stdev * 100) / np.average(target_dose), 3)}%")

    return scalar


def optimizer(filename=None):
    """
    Calls the optimization function - objectiveFunc().
    Returns the best pin thickness profile found.
    """

    sDDict = getSimData()
    # get the details of the initial guess stepped hedgehog
    # and the weights of the SOBPs
    init_thicknesses, init_weights, desired = genInitGuess(peaks=sDDict["peaks"], thicknesses=sDDict["thicknesses"])

    x0 = init_weights
    args = (init_thicknesses, desired, sDDict)

    bounds = [(0, 1)] * len(init_weights)

    options = {"maxiter": 1000}

    res = opt.minimize(objectiveFunc, x0, args=args, bounds=bounds, method="SLSQP", tol=1E-2, options=options)
    print(res)
    opt_weights = res.x
    depth_dose_sobp, pinData = genSOBP(init_thicknesses, opt_weights, sDDict, show=1, desired=desired, filename=filename)

    return pinData


def main():
    optimizer()


if __name__=="__main__":
    main()

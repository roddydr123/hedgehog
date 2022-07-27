import sys
import matplotlib.pyplot as plt
import numpy as np
from private.private import path
import pandas as pd
from scipy.integrate import simpson
from .SOBPwidth import getwidth
import scipy.interpolate as intp
from .loader import loader


plt.style.use('/mnt/c/users/david/documents/triumf/thesis/thesis.mplstyle')


def sobp():
    dataArr = []
    filenames = []

    lines = ["k-", "C2--", "C0-.", "k:", "k-", "k-", "k-", "k-", "k-", "k-", "k-", "k-", "k-", "k-"]

    # load in all the files and store their names
    for file in sys.argv[1:]:
        dataArr.append(np.array(loader(file)))
        filenames.append(file)

    fig, ax = plt.subplots()
    filenamess = ["Uncalibrated", "Calibrated", "2 cm", "0.6 cm", "J3 simulated", "J5 simulated"]

    doses = []
    areas = []
    sobps = []

    #low = 2.7
    #high = 3.5
    #low, high = input("please input the range for normalisation: ").split(' ')
    ax1 = ax.twinx()

    for i, sobp in enumerate(dataArr):

        # scale in x due to slabs angle
        diff = 0.5
        # angle = np.degrees(np.arctan(diff / 20))
        hyp = np.sqrt(diff**2 + 20**2)
        scaler = hyp / 20

        if ".csv" in filenames[i]:
            thresh = 0.2
            sobp[0] *= scaler
            #sobp[0] /= 10
        else:
            thresh = 0.1

        # move them so they start at zero on x axis
        a = np.argmax(sobp[1] > thresh * sobp[1].max())
        sobp[0] -= sobp[0][a]

        area = simpson(sobp[1], sobp[0])
        #sobp[1] /= area
        #sobp[1] /= sobp[1].max()

        if i == 0:
            y = sobp[1] #/  area * areas[0]
            x = sobp[0]
            ax.plot(x,y, lines[i], label=filenamess[i])
            ax.plot([0],[0], lines[i+1], label=filenamess[i+1])
        else:
            x = sobp[0]
            y = sobp[1] #/ sobp[1].max() * doses[0].max()
            ax1.plot(x,y, lines[i], label=filenamess[i])

        areas.append(area)
        doses.append(y)
        sobps.append(x)

        getwidth(sobp[0], sobp[1])
    
        #ax.plot(x,y, lines[i], label=filenamess[i])

    ax.set_xlabel("Depth in water (cm)")
    ax.set_ylabel("Pixel value")
    ax1.set_ylabel("Dose (Gy)")
    ax.set_xlim(0, 5)
    #ax.set_ylim(0, 15)

    ax.legend(frameon=False)

    plt.tight_layout()

    plt.show()


def profile():
    dataArr = []
    filenames = []

    # load in all the files and store their names
    for file in sys.argv[1:]:
        dataArr.append(np.array(loader(file)))
        filenames.append(file)

    #filenames = ["Reverse J2", "J2", "J5", "No HEDGEHOG"]
    lines = ["solid", "dotted", "dashed", "dashdot"]

    fig, ax = plt.subplots()

    for i, profile in enumerate(dataArr):
        # change units if needed
        if profile[0][-1] > 10:
            profile[0] /= 10

        # centre the peak on zero
        profile[0] -= profile[0][np.argmax(profile[1])]

        area = simpson(profile[1], profile[0])
        profile[1] /= area

        # find >99%
        slice = profile[1] >= 0.90 * profile[1].max()
        print(profile[0][slice][-1] - profile[0][slice][0])

        ax.plot(profile[0], profile[1], label=str(filenames[i]), color="k")

    ax.legend()
    ax.set_xlabel("Distance from maximum (cm)")
    ax.set_ylabel("Normalised dose")

    plt.show()


def main():
    if "pro" in ", ".join(sys.argv):
        profile()
    else:
        sobp()


if __name__ == "__main__":
    main()

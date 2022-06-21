import sys
import matplotlib.pyplot as plt
import numpy as np
from private.private import path
import pandas as pd
from scipy.integrate import simpson
from SOBPwidth import getwidth


plt.style.use('/mnt/c/users/david/documents/triumf/poster/poster.mplstyle')


def sobp():
    dataArr = []
    filenames = []

    lines = ["k-", "r-", "k--", "r--"]

    # load in all the files and store their names
    for file in sys.argv[1:]:
        dataArr.append(np.array(loader(file)))
        filenames.append(file)

    fig, ax = plt.subplots()
    filenamess = ["Normal measured", "Reversed measured", "Normal simulated", "Reversed simulated"]

    measured_avgs = []

    low = 2.7
    high = 3.5
    #low, high = input("please input the range for normalisation: ").split(' ')

    for i, sobp in enumerate(dataArr):

        # change units if needed
        #while sobp[0][-1] > 11:
        #    sobp[0] /= 10

        # scale in x due to slabs angle
        diff = 0.5
        # angle = np.degrees(np.arctan(diff / 20))
        hyp = np.sqrt(diff**2 + 20**2)
        scaler = hyp / 20

        if ".csv" in filenames[i]:
            thresh = 0.4
            sobp[0] *= scaler
            sobp[0] /= 10
        else:
            thresh = 0.1

        # move them so they start at zero on x axis
        a = np.argmax(sobp[1] > thresh * sobp[1].max())
        sobp[0] -= sobp[0][a]

        # while sobp[1].max() > 20:
        #    sobp[1] /= 10

        slice = (sobp[0] >= float(low)) & (sobp[0] <= float(high))

        # normalisation not great for films
        # area = simpson(sobp[1], sobp[0])
        # sobp[1] /= area

        measured_avgs.append(np.average(sobp[1][slice]))

        if i == 2:
            sobp[1] /= sobp[1].max() / measured_avgs[0]

        if i == 3:
            sobp[1] /= sobp[1].max() / measured_avgs[1]

        getwidth(sobp[0], sobp[1])

        if i == 50:
            ax.plot(sobp[0], sobp[1], label=filenames[i], color="k")
        #    #ax1.plot(sobp[0], sobp[1], label=filenames[i], color="k")
        else:
            #ax.plot(sobp[0], sobp[1], label=filenames[i], linestyle="dashed", color="k")
            ax.plot(sobp[0], sobp[1], lines[i], label=filenamess[i])
        #ax.plot(sobp[0], sobp[1], label=filenames[i])

    ax.legend()
    ax.set_xlabel("Depth in water (cm)")
    ax.set_ylabel("Dose (Gy)")
    ax.set_xlim(0, 5)

    #ax.set_ylim(-0.1, 1.1)

    ax.xaxis.set_tick_params(length=6, width=2)
    ax.yaxis.set_tick_params(length=6, width=2)

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


def loader(filename):
    """
    loads in data in a different way depending on whether it's a text file
    from FLUKA, a text file from film scans, or optimizer data.
    """

    if filename[-3:] == "txt":
        sim_array = np.genfromtxt(f'{path}data/{filename}', skip_header=1)

        if sim_array.shape[1] != 2:
            data = [sim_array[:, 0], sim_array[:, 2]]

        else:
            data = sim_array.T

    elif filename[-3:] == "npz":
        data = np.load(f'{path}data/{filename}')["depth_dose_sobp"]

    elif filename[-3:] == "csv":
        file = pd.read_csv(f'{path}film-scans/editing/{filename}', sep=",", names=["x", "calib", "uncalib"])
        data = [file["x"], file["calib"]]

    else:
        raise TypeError("Invalid filename or type")

    return data


def main():
    if "pro" in ", ".join(sys.argv):
        profile()
    else:
        sobp()


if __name__ == "__main__":
    main()

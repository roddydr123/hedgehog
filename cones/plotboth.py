import sys
import matplotlib.pyplot as plt
import numpy as np
from weightsCone import path


plt.style.use('/mnt/c/users/david/documents/triumf/poster/poster.mplstyle')


def sobp():
    dataArr = []
    filenames = []

    # load in all the files and store their names
    for file in sys.argv[1:]:
        dataArr.append(np.array(loader(file)))
        filenames.append(file)

    #filenames = ["Simulation result", "Resin small printer", "Resin industrial printer", "Nylon filament"]
    #filenames = ["Simulation result", "Wide pins (7mm)", "Medium pins (5mm)", "Thin pins (3mm)"]
    #filenames = ["Predicted by optimizer", "Simulation result"]

    fig, ax = plt.subplots(figsize=(11.8, 5))

    for i, sobp in enumerate(dataArr):

        # move them so they start at zero on x axis
        a = np.argmax(sobp[1] > 0.4 * sobp[1].max())
        sobp[0] -= sobp[0][a]

        # change units if needed
        if sobp[0][-1] > 10:
            sobp[0] /= 10

        # proper normalisation
        slice = (sobp[0] >= 3.2) & (sobp[0] <= 3.8)
        sobp[1] /= np.average(sobp[1][slice])

    ax.legend()
    ax.set_xlabel("Depth in water (cm)")
    ax.set_ylabel("Normalised dose (D_pl)")
    ax.set_xlim(0, 5)

    plt.tight_layout()

    plt.show()


def profile():
    dataArr = []
    filenames = []

    # load in all the files and store their names
    for file in sys.argv[1:]:
        dataArr.append(np.array(loader(file)))
        filenames.append(file)

    fig, ax = plt.subplots()

    for i, profile in enumerate(dataArr):
        # change units if needed
        if profile[0][-1] > 10:
            profile[0] /= 10

        # centre the peak on zero
        profile[0] -= profile[0][np.argmax(profile[1])]

        # proper normalisation
        #slice = (profile[0] >= -0.2) & (profile[0] <= 0.2)
        #profile[1] /= np.average(profile[1][slice])
        profile[1] /= profile[1].max()

        ax.plot(profile[0], profile[1], label=str(filenames[i]))

    ax.legend()
    ax.set_xlabel("Distance across beamspot (cm)")
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

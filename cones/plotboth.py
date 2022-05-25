import sys
import matplotlib.pyplot as plt
import numpy as np
from weightsCone import path


def main():
    dataArr = []
    filenames = []

    # load in all the files and store their names
    for file in sys.argv[1:]:
        dataArr.append(np.array(loader(file)))
        filenames.append(file)

    fig, ax = plt.subplots()

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

        ax.plot(sobp[0], sobp[1], label=str(filenames[i]))

    ax.legend()
    ax.set_xlabel("Depth (cm)")
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
        raise ValueError("Invalid filetype")
    
    return data


main()

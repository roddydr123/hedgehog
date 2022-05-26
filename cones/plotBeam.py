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

    for i, profile in enumerate(dataArr):

        # normalisation
        profile[1] /= profile[1].max()

        ax.plot(profile[0], profile[1], label=str(filenames[i]))

    ax.legend()
    ax.set_xlabel("Distance (cm)")
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

    else:
        raise TypeError("Invalid filename or type")

    return data


main()

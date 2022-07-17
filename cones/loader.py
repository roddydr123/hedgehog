import numpy as np
from private.private import path
import pandas as pd

def loader(filename):
    """
    loads in data in a different way depending on whether it's a text file
    from FLUKA, a text file from film scans, or optimizer data.
    """

    if filename[-3:] == "txt":
        sim_array = np.genfromtxt(f'{path}data/{filename}', skip_header=1)
        thresh = 0.1

        if sim_array.shape[1] != 2:
            data = [sim_array[:, 0], sim_array[:, 2], sim_array[:, 3]]

        else:
            data = sim_array.T

    elif filename[-3:] == "npz":
        data = np.load(f'{path}data/{filename}')["depth_dose_sobp"]
        thresh = 0.1

    elif filename[-3:] == "csv":
        file = pd.read_csv(f'{path}film-scans/editing/{filename}', sep=",", names=["x", "calib", "uncalib"])
        data = [file["x"] / 10, file["calib"]]
        thresh = 0.2

    else:
        raise TypeError("Invalid filename or type")

    # move so they start at zero
    a = np.argmax(data[1] > thresh * data[1].max())
    data[0] -= data[0][a]

    return np.array(data)
import numpy as np
import sys
from private.private import path


def main():

    no_bins = 200
    header = 2

    print("reading in...")

    data = np.genfromtxt(f'{path}data/{sys.argv[1]}', skip_header=header)

    fludet1slice = data[:no_bins]
    fludet2slice = data[602:802]
    fludet1 = sum(fludet1slice[:, 2])
    fludet2 = sum(fludet2slice[:, 2])
    print(fludet1 * 100 / fludet2)

    arr = fludet1slice[fludet1slice[:, 2] > 0]
    print(np.average(arr[:, 3] / arr[:, 2]))
    print(fludet1slice[:, 2].max())


main()

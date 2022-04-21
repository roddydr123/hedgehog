import sys
import matplotlib.pyplot as plt
import numpy as np


def main():
    target_files = [sys.argv[1], sys.argv[2]]

    fig, ax = plt.subplots()

    for i, filename in enumerate(target_files):
        sim_array = np.genfromtxt(f'data/{filename}.txt', skip_header=1)
        sim_sobp = [sim_array[:, 0], sim_array[:, 2]]

        # normalise the sobp
        sim_sobp[1] /= sim_sobp[1].max()

        # shift so starts at 0
        sim_sobp[0] -= sim_sobp[0].min()

        # pos02 needs an extra shift to line up
        if i == 1:
            sim_sobp[0] -= 0.02

        ax.plot(sim_sobp[0], sim_sobp[1], label=f"{filename}")

    ax.legend()
    ax.set_xlabel("Depth (cm)")
    ax.set_ylabel("Normalised dose")

    plt.show()


main()

import sys
import matplotlib.pyplot as plt
import numpy as np


def main():
    target_file = sys.argv[1]

    sim_array = np.genfromtxt(f'data/{target_file}.txt', skip_header=1)
    sim_sobp = [sim_array[:, 0], sim_array[:, 2]]

    depth_dose_sobp = np.load(f'data/{target_file}-gen.npz')["depth_dose_sobp"]

    # normalise the sobps
    depth_dose_sobp[1] /= depth_dose_sobp[1].max()
    sim_sobp[1] /= sim_sobp[1].max()

    # move the fluka sobp by 1
    sim_sobp[0] -= 1

    fig, ax = plt.subplots()
    ax.plot(depth_dose_sobp[0], depth_dose_sobp[1], label="optimized")
    ax.plot(sim_sobp[0], sim_sobp[1], label="FLUKA")
    ax.legend()
    ax.set_xlabel("Depth (cm)")
    ax.set_ylabel("Normalised dose")

    plt.show()


main()

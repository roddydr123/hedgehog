import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from weightsCone import path


def main():
    range, sobp_width = input("Give the range and the SOBP width: ").split()
    target_file = sys.argv[1]
    array = np.genfromtxt(f'{path}data/{target_file}.txt', skip_header=1)
    energies = array[:, 2]
    depths = array[:, 0]
    getwidth(depths, energies, range=float(range),
             sobp_width=float(sobp_width))
    # plotwidths()


def getwidth(depths, energies, range=None, sobp_width=None):
    peak = energies.max()
    peakarray = depths[energies >= 0.9 * peak]
    width = peakarray[-1] - peakarray[0]
    # SOBP width and maximum dE/dx value.
    print(f'SOBP width: {np.round(width * 10, 3)}mm, maximum: {peak}')
    # Entrance to peak ratio
    print(f'Entrance/peak: {np.round(100 * np.average(energies[0:5]) / peak, 1)}%')
    # 90% to 10% width (distal falloff)
    array = np.column_stack([depths, energies])
    PastPeak = array[energies.argmax():]
    UpLimRemove = PastPeak[PastPeak[:, 1] < 0.9 * peak]
    LowLimRemove = UpLimRemove[UpLimRemove[:, 1] > 0.1 * peak][:, 0]
    dropoff = LowLimRemove[-1] - LowLimRemove[0]
    print(f'90/10 dropoff takes {round(dropoff, 4)}cm')

    if range:
        # increase range because fluka sobp starts at 1
        range += 15
        target_region_slice = (depths <= range) &\
                              (depths >= range - sobp_width)
        target_dose = energies[target_region_slice]
        target_stdev = np.std(target_dose)
        print(f"target stdev: {np.round((target_stdev * 100) / np.average(target_dose), 3)}%")


def plotwidths():
    xdata = np.array([0, 0.25, 0.5, 0.59, 0.75, 1])
    thiccx = np.linspace(xdata[0], xdata[-1], 1000)
    ydata = np.array([3.13, 3.71, 4.54, 4.92, 5.83, 7.17])
    poptExp, pcovExp = curve_fit(exponential, xdata, ydata)
    perrExp = np.sqrt(np.diag(pcovExp))
    print(f'eqn is ae^bx + c: {poptExp} +- {perrExp}')

    fig, ax = plt.subplots()
    ax.scatter(xdata, ydata)
    ax.plot(thiccx, exponential(thiccx, *poptExp), "y")
    ax.set_xlabel("Pin length (cm)")
    ax.set_ylabel("SOBP width (mm)")
    plt.show()


def exponential(x, a, b, c):
    return a * np.exp(b * x) + c


if __name__ == "__main__":
    main()

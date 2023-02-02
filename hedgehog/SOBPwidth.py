import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def getwidth(depths, energies, range=None, sobp_width=None):
    peak = energies.max()
    peakarray = depths[energies >= 0.90 * peak]
    width = peakarray[-1] - peakarray[0]
    # SOBP width and maximum dE/dx value.
    print(f'SOBP width: {np.round(width, 3)}cm, maximum: {peak}')
    # Entrance to peak ratio
    print(f'Entrance/peak: '
          f'{np.round(100 * np.average(energies[0:5]) / peak, 1)}%')
    # 90% to 10% width (distal falloff)
    array = np.column_stack([depths, energies])
    PastPeak = array[energies.argmax():]
    UpLimRemove = PastPeak[PastPeak[:, 1] < 0.9 * peak]
    LowLimRemove = UpLimRemove[UpLimRemove[:, 1] > 0.1 * peak][:, 0]
    dropoff = LowLimRemove[-1] - LowLimRemove[0]
    d90 = LowLimRemove[0] # or peakarray[-1]
    d10 = LowLimRemove[-1]
    print(f'90/10 dropoff takes {round(dropoff, 4)}cm')
    print(f"90% distal point: {np.round(d90, 3)}")
    print(f"10% distal point: {np.round(d10, 3)}\n\n")

    if range:
        # increase range because fluka sobp starts at 1
        range += 15
        target_region_slice = (depths <= range) &\
                              (depths >= range - sobp_width)
        target_dose = energies[target_region_slice]
        target_stdev = np.std(target_dose)
        print(f"target stdev: "
              f"{np.round((target_stdev * 100) / np.average(target_dose), 3)}"
              f"%")

    return peakarray[0], width, dropoff

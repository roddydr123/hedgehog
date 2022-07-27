from hedgehog import hedgehog, undersim, SOBPeak
from private.private import path
import numpy as np


#h = hedgehog(2.5, 4.0, 20, "hedgehogJ5", tolerance=1E-3)

#h.viewDetails()
#h.generateGDML(5, 2.3)
#h.gdml2f()
#h.gdml2stl()

thicklist = [0.1, 0.19, 0.29, 0.38, 0.47, 0.57, 0.66, 0.75, 0.85, 0.94, 1.03, 1.13,
                1.22, 1.31, 1.41, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2,
                2.3, 2.4, 2.5, 2.6, 2.7, 2.8]

us = undersim(thicklist, "..")


def analyse():
    with open(path+"minsum - Copy.txt", "r") as file:
        lines = file.readlines()
    lis = []
    for line in lines:
        lis.append(float(line))

    lis = np.array(lis)

    print(np.std(lis))
    print(np.average(lis))
    print(len(lis))

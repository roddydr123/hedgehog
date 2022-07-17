from hedgehog import hedgehog
from private.private import path
import numpy as np


h = hedgehog(2.5, 4.0, 20, "hedgehogJ5", tolerance=1E-3)

#h.viewDetails()
h.generateGDML(5, 2.3)
#h.gdml2f()
#h.gdml2stl()


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

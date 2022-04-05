import numpy as np


"""Choose the parameters for the SOBP"""
rho = 1             # density of absorbing medium, 1 for water
D0 = 1              # desired height of SOBP
p = 1.8
alpha = 1.9E-3
SOBPwidth = 0.6     # set the desired SOBP width in cm
db = 4.0              # desired depth of distal edge in water
steps = 8           # desired no. blocks/weights
waterEquiv = 1.158  # water equivalent thickness for PMMA
d_across_pinbase = 0.1  # set the short diameter of the pinbase hexagons
baseEdges = 0.7         # x and y size of the base you want to tile


a = alpha**(1 / p)  # simplifying equation
da = db - SOBPwidth
Delta = SOBPwidth / steps


def baseQuad(x):
    return x**2


def blockSpecs(steps=steps):
    weights = calcWeights(steps=steps)
    height = blockHeight(steps=steps)
    desired = [db, SOBPwidth]

    return height, weights, desired


def calcWeights(steps=steps):
    """
    Uses Bortfeld 1996 method to calculate the weights of the
    pristine BPs composing the desired SOBP.
    """
    Wr = rho * D0 * (p**2 * a * np.sin(np.pi / p) / np.pi * (p - 1))
    WrPrim = Wr * (Delta / 2)**(1 - (1 / p))
    weights = [WrPrim]
    for i in range(1, steps + 1):
        R = db - (Delta * i)
        Wr_i = Wr * ((db - R + (Delta / 2))**(1 - (1 / p))
                     - (db - R - (Delta / 2))**(1 - (1 / p)))
        weights.append(Wr_i)
    weights = np.array(weights)
    norm = weights / weights[0]

    return norm


def blockHeight(steps=steps):
    return SOBPwidth / steps


def wToRadii(weights):

    A_pinbase = np.sqrt(3) * d_across_pinbase**2 / 2

    gamma = A_pinbase / np.sum(weights)

    eAs = gamma * weights

    As = np.zeros_like(eAs)

    for i in range(len(weights)):
        index = len(weights) - (i + 1)
        A = np.sum(eAs[index:])
        As[index] = A

    radii = np.sqrt(As / np.pi)

    return radii

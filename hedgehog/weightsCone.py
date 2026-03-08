import numpy as np

from hedgehog.static_classes import SOBPeak_cls


def blockSpecs(SOBPeak: SOBPeak_cls) -> tuple:
    weights = calcWeights(SOBPeak)
    height = blockHeight(SOBPeak)
    desired = [SOBPeak.range, SOBPeak.width]

    return height, weights, desired


def calcWeights(SOBPeak: SOBPeak_cls) -> np.ndarray:
    """
    Uses Bortfeld 1996 method to calculate the weights of the
    pristine BPs composing the desired SOBP.
    """
    db = SOBPeak.range
    steps = SOBPeak.steps
    SOBPwidth = SOBPeak.width

    rho = 1  # density of absorbing medium, 1 for water
    D0 = 1  # desired height of SOBP
    p = 1.8
    alpha = 1.9e-3

    a = alpha ** (1 / p)  # simplifying equation
    Delta = SOBPwidth / steps

    Wr = rho * D0 * (p**2 * a * np.sin(np.pi / p) / np.pi * (p - 1))
    WrPrim = Wr * (Delta / 2) ** (1 - (1 / p))
    weights = [WrPrim]
    for i in range(1, steps + 1):
        R = db - (Delta * i)
        Wr_i = Wr * ((db - R + (Delta / 2)) ** (1 - (1 / p)) - (db - R - (Delta / 2)) ** (1 - (1 / p)))
        weights.append(Wr_i)
    weights = np.array(weights)
    norm = weights / weights[0]

    return norm


def blockHeight(SOBPeak: SOBPeak_cls) -> float:
    return SOBPeak.width / SOBPeak.steps


def wToRadii(weights: np.ndarray, d_across_pinbase: float) -> np.ndarray:

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

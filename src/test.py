import matplotlib.pyplot as plt
import numpy as np
from psutil import cpu_freq
import random

np.random.seed(19680801)
def rando():
    while True:
        number = random(0.0, 0.50)
        print(number)
        return numbergo

def grafico():
    dt = rando()
    t = np.arange(0, 10, dt)
    nse = np.random.randn(len(t))
    r = np.exp(-t / 0.05)

    cnse = np.convolve(nse, r) * dt
    cnse = cnse[: len(t)]
    s = 0.1 * np.sin(2 * np.pi * t) + cnse

    fig, (ax0, ax1) = plt.subplots(2, 1)
    ax0.plot(t, s)
    ax1.psd(s, 512, 1 / dt)

    plt.show()

grafico()
from .UI import Interface
from collections import defaultdict
import pygame
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
import scipy.signal as signal


def Analyse(sample_path, size_markers=None):
    if not size_markers:
        size_markers = [15000, 10000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1500, 1000,
                        850, 650, 500, 400, 300, 200, 100]

    selections = Interface(sample_path).selections
    _DetermineBands(selections, size_markers)


def _DetermineBands(selections, size_markers):
    well_pos, bands, markers = selections

    # INFO
    print(f"Using {len(markers)} DNA fragment markers.")

    # Sort into wells
    well_slots = defaultdict(list)
    for band in bands:
        x, y = band
        well_slots[x].append(y - well_pos)
    marker_bands = [pos[1] - well_pos for pos in markers]

    # INFO
    print(f"Calculating {len(bands)} wells and {sum([len(value) for _, value in well_slots.items()])} bands.")

    x = np.array(marker_bands)
    y = np.array(size_markers[:len(marker_bands)])
    log_x = np.log(x)
    log_y = np.log(y)
    curve_fit = np.polyfit(x, log_y, 1)
    m, c = curve_fit
    derive_y = np.exp(c) * np.exp(m * x)

    fig, ax = plt.subplots()
    plt.scatter(x, y)
    plt.plot(x, derive_y)

    ax.set_title("Calibration Plot")
    ax.set_yscale("log")
    ax.set_ylabel("Size DNA (kb)")
    ax.set_xlabel("Distance migrated (px)")
    plt.show()

    for key, value in well_slots.items():
        well_slots[key] = [np.exp(c) * np.exp(m * band) for band in value]

    while any([value for value in well_slots.values()]):
        printed = ""
        for index, band in well_slots.items():
            if band:
                printed += f"{int(band.pop(0))} kBp".rjust(10, " ")
            else:
                printed += " " * 10
        print(printed)

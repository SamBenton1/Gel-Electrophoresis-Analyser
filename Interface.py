"""
Interface.py
Version == 1.0.0

Contains the interface for selecting the wells, bands and markers in order to calculated the calibration plot. If
the script is run as __main__ it will open a dialog for the selection. The results will be saved in a results.pickle
file which contains the serialised data returned from the UI. Alternatively the OpenUI() method can be run which returns
the results from the selections.
    The results are returned as a dictionary which contains the wells y coordinate and the position of the markers
and the bands.

"""

import pickle
import logging
import pygame
from PIL import Image
import numpy as np
import scipy.signal as signal
from matplotlib import pyplot as plt

GRAPH = True

# RGB colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Peak finding variables
BRIGHTNESS_THRESHOLD = 80
PEAK_WIDTH = 2
PEAK_SEPARATION = 4
OFFSET = 1
INTERVALS = 7

# logging.basicConfig(level=logging.INFO)


def _GraphBandDetection(pixel_array, peaks):
    """
    Plots the graph of rgb intensity for each well selected in the UI. Helps to
    visualise how the bands were found and what tweaking to the constants
    may be required for more accurate band detection.

    :param pixel_array: The array of pixels for the particular x coordinate.
    :param peaks: The peaks calculated by the Scipy algorithm
    :return: None
    """
    # Plot the pixel array
    plt.plot(pixel_array)
    plt.ylabel("Pixel Value")
    plt.xlabel("Pixel y-coordinate")

    # Plot peaks
    for peak in peaks[0]:
        plt.scatter(peak, pixel_array[peak], c="r")
    plt.show()


def OpenUI(sample_path):

    # Load in the gel image
    pillow_image: Image.Image = Image.open(sample_path)
    pillow_image = pillow_image.convert(mode="L")  # Convert gel image to gray scale
    gel_pixels = pillow_image.load()
    gel_image = pygame.image.load(sample_path)

    # UI Setup
    *_, width, height = gel_image.get_rect()
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("PCR Analyser")
    pygame.display.set_icon(pygame.image.load("resources/icon.jpg"))
    logging.info("Interface window started")

    pygame.font.init()
    font = pygame.font.SysFont("arial", 20)

    # UI variables
    well_position = 0  # y coordinate of the well marker line.
    selected_action = "Well Position"
    marker_coordinates = []
    band_coordinates = []

    # Finds the bands using band intensity
    def FindBands() -> list:
        """
        Uses Scipy signal.find_peaks() method to find point of high rgb intensity these are used
        to determine the y position of the bands. The method then returns a list of band coordinates.

        :return: List of tuple coordinates
        """
        mouse_x, mouse_y = event.pos
        x_samples = [mouse_x - OFFSET + OFFSET * i for i in range(INTERVALS * 2 + 1)]

        # Generate pixel array
        pixel_array = [(sum([gel_pixels[x, y] for x in x_samples]) // len(x_samples)) for y in
                       range(height)]

        # Depreciated - Uses sum of rgb values rather than grayscale
        # pixel_array = [(sum([sum(gel_pixels[x, y]) for x in x_samples]) // len(x_samples)) for y in
        #                range(height)]

        # Find peaks
        peaks = (signal.find_peaks(
            np.array(pixel_array),
            height=BRIGHTNESS_THRESHOLD,
            distance=PEAK_SEPARATION,
            width=PEAK_WIDTH
        ))

        # Graph the bands as they are selected
        if GRAPH:
            logging.info("Pixel array graphing is on")
            _GraphBandDetection(pixel_array, peaks)

        peak_points = [(mouse_x, peak) for peak in peaks[0]]
        return peak_points

    # Called each refresh cycle to update the game window
    def RedrawGameWindow():
        win.blit(gel_image, (0, 0))
        pygame.draw.line(win, (255, 0, 0), (0, well_position), (width, well_position))  # Draw well position line

        # Draw the markers and bands.
        for marker in marker_coordinates:
            pygame.draw.circle(win, BLUE, marker, 3)
        for band in band_coordinates:
            pygame.draw.circle(win, RED, band, 3)

        # Draw the indication of the selected action
        rendered_font = font.render(selected_action, True, WHITE)
        win.blit(rendered_font, (5, 5))

    # UI Loop
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if selected_action == "Well Position":
                    well_position = event.pos[1]  # Set the well_position to that of the mouse.
                elif selected_action == "Markers":
                    marker_coordinates = FindBands()
                elif selected_action == "Bands":
                    band_coordinates.extend(FindBands())

            elif event.type == pygame.KEYDOWN:
                if event.unicode == "w":
                    selected_action = "Well Position"
                elif event.unicode == "m":
                    selected_action = "Markers"
                elif event.unicode == "b":
                    selected_action = "Bands"

                # To close the window and perform calculation
                elif event.key == pygame.K_RETURN:
                    pygame.quit()
                    data = {
                        "well_position": well_position,
                        "markers": marker_coordinates,
                        "bands": band_coordinates
                    }
                    if not all(data.values()):
                        logging.warning("One or more of the data were not selected in the interface")

                    return data

        RedrawGameWindow()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    results = OpenUI(r"Gels\Gel 1(4).jpg")
    with open("results.pickle", "wb") as data_file:
        pickle.dump(results, data_file)

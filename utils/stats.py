import numpy as np

def gaussian_2d(x, y, x0, y0, sigma_x, sigma_y, amplitude):
    return amplitude * np.exp(-(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2)))

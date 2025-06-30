from .Thermal import BaseThermal
import numpy as np

class AllenThermal(BaseThermal):
    # intialize the class, with the center of the updraft, x, y, the updraft strength scale factor, wstar, the multipliers for wstar, wgain, the multipliers for the average radius, rgain, the updraft height, zi
    def __init__(self, x, y, wstar, wgain=1, rgain=1, zi=1400):
        self.x = x
        self.y = y
        self.wstar = wstar
        self.wgain = wgain
        self.rgain = rgain
        self.zi = zi

    def get_strength_at(self, x, y, z):
        # Define updraft shape factors
        r1r2shape = np.array([0.1400, 0.2500, 0.3600, 0.4700, 0.5800, 0.6900, 0.8000])
        Kshape = np.array([
            [1.5352, 2.5826, -0.0113, -0.1950, 0.0008],
            [1.5265, 3.6054, -0.0176, -0.1265, 0.0005],
            [1.4866, 4.8356, -0.0320, -0.0818, 0.0001],
            [1.2042, 7.7904, 0.0848, -0.0445, 0.0001],
            [0.8816, 13.9720, 0.3404, -0.0216, 0.0001],
            [0.7067, 23.9940, 0.5689, -0.0099, 0.0002],
            [0.6189, 42.7965, 0.7157, -0.0033, 0.0001]
        ])

        # Calculate distance to the updraft
        dist = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        
        # Calculate average updraft size
        zzi = z / self.zi
        rbar = (0.102 * zzi^(1 / 3)) * (1 - (0.25 * zzi)) * self.zi

        # Calculate average updraft strength
        wtbar = (zzi ^ (1 / 3)) * (1 - 1.1 * zzi) * self.wstar


        # Calculate inner and outer radius of rotated trapezoid updraft
        r2 = rbar * self.rgain
        if r2 < 10:
            r2	= 10
        if r2 > 600:
            r1r2 = 0.0011 * r2 + 0.14
        else:
            r1r2 = 0.8
        r1 = r1r2 * r2
        
        # Multiply average updraft strength by wgain for this updraft
        wt = wtbar * self.wgain

        # Calculate strength at center of rotated trapezoid updraft
        wc = (3 * wt * ((r2 ** 3) - (r2 ** 2) * r1)) / ((r2 ** 3) - (r1 ** 3))

        # Calculate updraft velocity
        r = dist
        rr2 = r / r2

        if z < self.zi:
            # Determine shape coefficients based on r1/r2 ratio
            if r1r2 < .5 * (r1r2shape[0] + r1r2shape[1]):
                ka, kb, kc, kd = Kshape[0, :4]
            elif r1r2 < .5 * (r1r2shape[1] + r1r2shape[2]):
                ka, kb, kc, kd = Kshape[1, :4]
            elif r1r2 < .5 * (r1r2shape[2] + r1r2shape[3]):
                ka, kb, kc, kd = Kshape[2, :4]
            elif r1r2 < .5 * (r1r2shape[3] + r1r2shape[4]):
                ka, kb, kc, kd = Kshape[3, :4]
            elif r1r2 < .5 * (r1r2shape[4] + r1r2shape[5]):
                ka, kb, kc, kd = Kshape[4, :4]
            else:
                ka, kb, kc, kd = Kshape[5, :4]

            # Calculate updraft velocity using shape coefficients
            ws = wc * (ka * rr2 ** 2 + kb * rr2 + kc * rr2 ** 3 + kd * rr2 ** 4)
        else:
            ws = 0



        return w

    def get_strength_at_points(self, points):
        return np.array([self.get_strength_at(x, y, z) for x, y, z in points])
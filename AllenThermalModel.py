from .Thermal import BaseThermal
import numpy as np

class AllenThermalModel(BaseThermal):
    """
    Extended Allen Thermal Model

    This Python implementation is based on the provided MATLAB code (run_model2_3).
    It models a thermal using a rotated trapezoid updraft shape, and optionally
    includes sink behavior outside the updraft core.

    Attributes:
        xt (array-like): x-coordinates of updraft centers (m)
        yt (array-like): y-coordinates of updraft centers (m)
        wstar (float): updraft strength scale factor (m/s)
        wgain (array-like): vector of multipliers for wstar
        rgain (array-like): vector of multipliers for the average radius
        zi (float): updraft height (m)
        A (float): area of test space (m^2)
        sflag (int): 0 = no sink outside updrafts, 1 = sink outside updrafts
    """

    def __init__(self, xt, yt, wstar, wgain=1, rgain=[1], zi=1000, A=1000000, sflag=0):
        """
        Initialize an AllenThermalModel.

        Args:
            xt (array-like): x-coordinates of updraft centers
            yt (array-like): y-coordinates of updraft centers
            wstar (float): updraft strength scale factor (m/s)
            wgain (array-like, optional): multipliers for wstar. Defaults to ones.
            rgain (array-like, optional): multipliers for the average radius. Defaults to ones.
            zi (float, optional): updraft height (m). Defaults to 1000.
            A (float, optional): area of test space (m^2). Defaults to 1000000.
            sflag (int, optional): 0 = no sink, 1 = enable sink outside updraft. Defaults to 0.
        """
        self.xt = np.array(xt, dtype=float)
        self.yt = np.array(yt, dtype=float)
        self.wstar = float(wstar)
        self.wgain = np.array(wgain, dtype=float) if wgain is not None else np.ones(len(xt))
        self.rgain = np.array(rgain, dtype=float) if rgain is not None else np.ones(len(xt))
        self.zi = float(zi)
        self.A = float(A)
        self.sflag = int(sflag)

    def get_strength_at(self, x, y, z):
        """
        Compute the updraft (or sink) velocity at position (x, y, z).

        Args:
            x (float): x position
            y (float): y position
            z (float): z position

        Returns:
            float: updraft velocity; if sink is enabled,
            regions beyond the updraft core may return negative velocities
        """

        # Convert inputs to float for consistent handling
        
        # Allen's shape factors
        r1r2shape = np.array([0.1400, 0.2500, 0.3600, 0.4700, 0.5800, 0.6900, 0.8000])
        Kshape = np.array([
            [1.5352,  2.5826,  -0.0113, -0.1950,  0.0008],
            [1.5265,  3.6054,  -0.0176, -0.1265,  0.0005],
            [1.4866,  4.8356,  -0.0320, -0.0818,  0.0001],
            [1.2042,  7.7904,   0.0848, -0.0445,  0.0001],
            [0.8816, 13.9720,   0.3404, -0.0216,  0.0001],
            [0.7067, 23.9940,   0.5689, -0.0099,  0.0002],
            [0.6189, 42.7965,   0.7157, -0.0033,  0.0001]
        ])

        # Distances to each updraft center
        dist = np.sqrt((x - self.xt)**2 + (y - self.yt)**2)

        # z / zi
        zzi = z / self.zi

        # Average updraft size
        rbar = (0.102 * (zzi ** (1/3.0))) * (1 - 0.25 * zzi) * self.zi

        # Average updraft strength
        wtbar = (zzi ** (1/3.0)) * (1 - 1.1 * zzi) * self.wstar

        # Nearest updraft index
        upused = np.argmin(dist)

        # Outer radius (r2) with random gain
        print(self.rgain)
        r2 = rbar * self.rgain
        r2 = max(r2, 10)  # limit small updrafts to 20m diameter

        # Inner radius ratio
        if r2 < 600:
            r1r2 = 0.0011 * r2 + 0.14
        else:
            r1r2 = 0.8
        r1 = r1r2 * r2

        # Weighted updraft strength
        wt = wtbar * self.wgain[upused]

        # Strength at center
        numerator = 3.0 * wt * (r2**3 - (r2**2)*r1)
        denominator = (r2**3) - (r1**3)
        if abs(denominator) < 1e-6:
            wc = 0.0
        else:
            wc = numerator / denominator

        # Distance for active updraft
        r_used = dist[upused]
        rr2 = r_used / r2

        # Default vertical velocity
        w_updraft = 0.0

        # Within boundary layer
        if z < self.zi:
            # Determine shape coefficients
            if r1r2 < 0.5 * (r1r2shape[0] + r1r2shape[1]):
                ka, kb, kc, kd = Kshape[0, :4]
            elif r1r2 < 0.5 * (r1r2shape[1] + r1r2shape[2]):
                ka, kb, kc, kd = Kshape[1, :4]
            elif r1r2 < 0.5 * (r1r2shape[2] + r1r2shape[3]):
                ka, kb, kc, kd = Kshape[2, :4]
            elif r1r2 < 0.5 * (r1r2shape[3] + r1r2shape[4]):
                ka, kb, kc, kd = Kshape[3, :4]
            elif r1r2 < 0.5 * (r1r2shape[4] + r1r2shape[5]):
                ka, kb, kc, kd = Kshape[4, :4]
            elif r1r2 < 0.5 * (r1r2shape[5] + r1r2shape[6]):
                ka, kb, kc, kd = Kshape[5, :4]
            else:
                ka, kb, kc, kd = Kshape[6, :4]

            # Calculate a basic shape function over 0 <= rr2 <= 1
            if rr2 < 1.0:
                # Follow the shape from Allen's code: a logistic-like approach
                # or polynomial approach. The original code uses expansions; we adapt:
                # Here we define a simplistic polynomial approach akin to the piecewise definition.
                in_ = rr2
                shape_val = ka * in_**2 + kb * in_ + kc * in_**3 + kd * in_**4
                # The center of the thermal is w = wc, gradually diminishing to zero near r2
                w_updraft = wc * max(shape_val, 0.0)
            else:
                # Outside thermal's radius => possible sink
                if self.sflag == 1:
                    # For sink, define a negative velocity. 
                    # Example: ~10% of core strength, negative.
                    # You may adjust this fraction or any formula as needed.
                    w_updraft = -0.1 * abs(wc)
                else:
                    w_updraft = 0.0
        else:
            # Above boundary layer => no updraft
            if self.sflag == 1:
                # Optionally define a uniform sink
                w_updraft = -0.1 * abs(wc)
            else:
                w_updraft = 0.0

        return w_updraft

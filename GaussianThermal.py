from .utils.stats import gaussian_2d
import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
from .Thermal import BaseThermal



class GaussianThermal(BaseThermal):
    center = None
    strength = None
    diameter = None

    def __init__(self, x=0, y=0, strength=5, diameter=20):
        self.center = (x, y)
        self.strength = strength
        self.diameter = diameter

    def get_strength_at(self, x, y, z=None):
        return gaussian_2d(x, y, self.center[0], self.center[1], sigma_x=self.__get_sigma__(), sigma_y=self.__get_sigma__(), amplitude=self.strength)


    def get_strength_at_points(self, points):
        points = np.array(points)
        return gaussian_2d(points[:, 0], points[:, 1], self.center[0], self.center[1], sigma_x=self.__get_sigma__(), sigma_y=self.__get_sigma__(), amplitude=self.strength)

    def get_center(self):
        return self.center

    def get_diameter(self):
        return self.diameter

    def get_strength(self):
        return self.strength

    def __get_sigma__(self):
        return self.diameter / 2.355

    def plot(self):
        x = np.linspace(-self.diameter * 2, self.diameter * 2, 400)
        y = np.linspace(-self.diameter * 2, self.diameter * 2, 400)
        x, y = np.meshgrid(x, y)

        # Gaussian
        z = gaussian_2d(x, y, 0, 0, self.__get_sigma__(),
                        self.__get_sigma__(), self.strength)

        # Plot
        plt.contourf(x, y, z, levels=50, cmap='viridis')
        plt.colorbar(label='Thermal Strength')
        plt.title('Thermal modelled as 2D Gaussian')
        plt.xlabel('X')
        plt.ylabel('Y')


class GaussianThermalDistribution:
    mixture = None
    def __init__(self, centers, strengths, diameters):
        self.mixture = []
        for i in range(len(centers)):
            thermal = GaussianThermal(centers[i][0], centers[i]
                              [1], strengths[i], diameters[i])
            self.mixture.append(thermal)

    def __init__(self):
        self.mixture = []

    def get_strength_at(self, x, y, z=None):
        strength = 0
        for thermal in self.mixture:
            strength += thermal.get_strenght_at(x, y)
        return strength
    
    def get_strength_at_points(self, points):
        points = np.array(points)
        strength = np.zeros(points.shape[0])
        for thermal in self.mixture:
            strength += thermal.get_strength_at_points(points)
        return strength        

    def get_thermals(self):
        return self.mixture

    def add_thermal(self, thermal):
        self.mixture.append(thermal)

    def plot(self):
        x = np.linspace(-200, 200, 400)
        y = np.linspace(-200, 200, 400)
        x, y = np.meshgrid(x, y)

        # Gaussian
        z = np.zeros_like(x)
        for thermal in self.mixture:
            z += gaussian_2d(x, y, thermal.get_center()[0], thermal.get_center()[1], sigma_x=thermal.__get_sigma__(),
                            sigma_y=thermal.__get_sigma__(), amplitude=thermal.get_strength())

        # Plot
        plt.contourf(x, y, z, levels=50, cmap='viridis')
        plt.colorbar(label='Thermal Strength')
        plt.title('Thermal modelled as 2D Gaussian')
        plt.xlabel('X')
        plt.ylabel('Y')


class GPPredictor:
    kernel = RBF(length_scale=25.0)
    gp = GaussianProcessRegressor(kernel=kernel, alpha=0.1)
    
    def __init__(self):
        self.gp = GaussianProcessRegressor(kernel=self.kernel, alpha=0.1)



    def fit(self, X, y):
        self.gp.fit(X, y)

    def predict(self, X, return_std=False):
        return self.gp.predict(X, return_std=return_std)

    def visualize(self):
        x,y = np.meshgrid(np.linspace(-200, 200, 200), np.linspace(-200, 200, 200))
        points = np.vstack([x.ravel(), y.ravel()]).T
        strength, _ = self.predict(points, return_std=True)
        plt.figure(figsize=(15, 10))
        plt.subplot(2, 2, 1)
        plt.contourf(x, y, strength.reshape(x.shape), levels=50, cmap='viridis')
        plt.colorbar(label='Thermal Strength')
    


class TimeVaryingGaussianThermalDistribution:
    thermal_distribution = None

    def __init__(self, thermal_distribution, shift_direction, shift_speed):
        self.thermal_distribution = thermal_distribution

    
    def get_strength_at(self, x, y, t):
        thermal_distribution_at_t = self.thermal_distribution
        for thermal in thermal_distribution_at_t.get_thermals():
            thermal.center = (thermal.center[0] + t * self.shift_speed, thermal.center[1] + t * self.shift_speed)
        return thermal_distribution_at_t.get_strength_at(x, y)


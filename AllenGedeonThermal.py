from .Thermal import BaseThermal, ThermalMixture

import numpy as np
import matplotlib.pyplot as plt

class AllenGedeonThermal(BaseThermal):
    def __init__(self, strength, x_center, y_center, thermal_height, diameter):
        self.strength = strength
        self.x_center = x_center
        self.y_center = y_center
        self.thermal_height = thermal_height
        self.diameter = diameter

    def get_relative_height(self, z):
        return z / self.thermal_height
    

    def get_z_thermal_radius(self, z):
        return 0.102 * (self.get_relative_height(z) ** (1 / 3)) * (1 - (0.25 * self.get_relative_height(z))) * self.thermal_height
    
    def get_z_max_thermal_strength(self, z):
        scale_factor = 2.2
        return scale_factor * (self.get_relative_height(z) ** (1 / 3)) * (1 - 1.1 * self.get_relative_height(z)) * self.strength
    
    def get_strength_at(self, x, y, z):
        # Implement the specific formula for Allen-Gedeon thermal strength
        return self.strength * np.exp(-((x - self.x_center)**2 + (y - self.y_center)**2 + (z - self.z_center)**2))
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    

    def visualize_thermal_structure(self):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 6))
        # visualize the change of themral strength with height
        z = np.linspace(0, self.thermal_height, 1000)
        ax[0].plot(self.get_z_max_thermal_strength(z), z)
        # plot dotted line for the maximum thermal strength and 0
        ax[0].axvline(x=self.strength, linestyle='--', color='k')
        ax[0].axvline(x=0, linestyle='--', color='k')
        ax[0].set_ylabel('Height  [m]')
        ax[0].set_xlabel('Thermal strength [m/s]')
        ax[0].set_title(f'Thermal strength = {self.strength} m/s')

        # visualize the change of thermal radius with height
        ax[1].plot(self.get_z_thermal_radius(z), z)
        ax[1].set_ylabel('Height [m]')
        ax[1].set_xlabel('Thermal radius [m]')
        ax[1].set_title(f'Thermal diameter = {self.diameter} m')

        fig.suptitle(f'Allen Gedeon Thermal with {self.thermal_height} m height')
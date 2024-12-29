from .Thermal import BaseThermal
from abc import abstractmethod, ABC
import numpy as np

class GedeonThermal(BaseThermal):
    def __init__(self, x=0, y=0, strength=5, diameter=20):
        self.center = (x, y)
        self.strength = strength
        self.diameter = diameter
    
    def get_distance_from_center(self, x, y):
        return np.sqrt((x - self.center[0])**2 + (y - self.center[1])**2)
    
    def get_strength_at_points(self, points):
        points = np.array(points)
        return self.get_strength_at(points[:, 0], points[:, 1], points[:, 2])

    def get_strength_at(self, x, y, z):
        r = self.get_distance_from_center(x, y)
        return self.strength * np.exp(-1* (r / self.diameter) ** 2) * (1 - (r / self.diameter) ** 2)
from abc import abstractmethod, ABC
import matplotlib.pyplot as plt
import numpy as np


class BaseThermal(ABC):
    @abstractmethod
    def get_strength_at(self, x, y, z):
        pass
    
    def get_strength_at_points(self, points):
        points = np.array(points)
        return self.get_strength_at(points[:, 0], points[:, 1], points[:, 2])

    def plot2D(self, x_range, y_range, z, v_min=None, v_max=None, ax=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        x = np.linspace(x_range[0], x_range[1], 400)
        y = np.linspace(y_range[0], y_range[1], 400)
        x, y = np.meshgrid(x, y)
        strengths = self.get_strength_at(x=x, y=y, z=z)
        if v_min is not None and v_max is not None:
            contourf = ax.contourf(x, y, strengths, levels=100, cmap='viridis', vmin=v_min, vmax=v_max)
        else:
            contourf = ax.contourf(x, y, strengths, levels=100, cmap='viridis')
        cbar = plt.colorbar(contourf, ax=ax, label='Thermal Strength [m/s]')

    def plot3D(self, x_range, y_range, z, z_range=[0, 10], v_min=None, v_max=None, ax=None):
        if ax is None:
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
        x = np.linspace(x_range[0], x_range[1], 400)
        y = np.linspace(y_range[0], y_range[1], 400)
        x, y = np.meshgrid(x, y)
        strengths = self.get_strength_at(x=x, y=y, z=z)
        if v_min is not None and v_max is not None:
            surf = ax.plot_surface(x, y, strengths, cmap='viridis', vmin=v_min, vmax=v_max)
        else:
            surf = ax.plot_surface(x, y, strengths, cmap='viridis', vmin=-(np.max(np.abs(strengths))), vmax=np.max(np.abs(strengths)))
        # add colorbar
        cbar = fig.colorbar(surf, ax=ax)
        cbar.set_label('Thermal Strength [m/s]')
        ax.set_zlim(z_range[0], z_range[1])


class ThermalMixture():
    def __init__(self, thermals = []):
        self.thermals = thermals

    def get_strength_at(self, x, y, z):
        results = [thermal.get_strength_at(x, y, z) for thermal in self.get_thermals()]
        return sum(results)

    def get_strength_at_points(self, points):
        return [self.get_strength_at(point[0], point[1], point[2]) for point in points]

    def get_thermals(self):
        return self.thermals

    def add_thermal(self, thermal):
        self.thermals.append(thermal)

    def remove_thermal(self, thermal):
        self.thermals.remove(thermal)

    def plot2D(self, x_range, y_range, z, ax=None, v_min=None, v_max=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        x = np.linspace(x_range[0], x_range[1], 400)
        y = np.linspace(y_range[0], y_range[1], 400)
        x, y = np.meshgrid(x, y)
        strengths = self.get_strength_at(x=x, y=y, z=z)
        if v_min is not None and v_max is not None:
            contourf = ax.contourf(x, y, strengths, levels=100, cmap='viridis', vmin=v_min, vmax=v_max)
        else:
            contourf = ax.contourf(x, y, strengths, levels=100, cmap='viridis', vmin=-(np.max(np.abs(strengths))), vmax=np.max(np.abs(strengths)))
        cbar = plt.colorbar(contourf, ax=ax)
        cbar.set_label('Thermal Strength [m/s]')

    def plot3D(self, x_range, y_range, z, z_range=[-1, 5], v_min=None, v_max=None, ax=None):
        if ax is None:
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
        x = np.linspace(x_range[0], x_range[1], 1000)
        y = np.linspace(y_range[0], y_range[1], 1000)
        x, y = np.meshgrid(x, y)
        strengths = self.get_strength_at(x=x, y=y, z=z)
        if v_min is not None and v_max is not None:
            surf = ax.plot_surface(x, y, strengths, cmap='viridis', vmin=v_min, vmax=v_max)
        else:
            surf = ax.plot_surface(x, y, strengths, cmap='viridis', vmin=-(np.max(np.abs(strengths))), vmax=np.max(np.abs(strengths)))
        cbar = fig.colorbar(surf, ax=ax)
        cbar.set_label('Thermal Strength [m/s]')
        ax.set_zlim(z_range[0], z_range[1])

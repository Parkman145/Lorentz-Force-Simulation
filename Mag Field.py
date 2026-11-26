import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from dataclasses import dataclass
import pyqtgraph.opengl as gl
from time import sleep


import pint
u = pint.UnitRegistry()

pg.mkQApp()

## make a widget for displaying 3D objects
view = gl.GLViewWidget()


# Constants
u_0 = 1.26e-9 * u.N/u.A**2
pi = u.pi
small_dist = 0.00001 * u.m
k = 8.99*10**9 * u.N*u.m**2/u.C**2



class World:
    objects = []

    @classmethod
    def add(cls, object):
        cls.objects.append(object)
    @classmethod 
    def elec_field(cls, coords) -> pint.Quantity:
        electric_field = np.zeros_like(coords) * u.V/u.m
        for elem in cls.objects:
            electric_field = electric_field + elem.elec_field(coords)

        return electric_field
    @classmethod
    def mag_field(cls, coords) -> pint.Quantity:
        mag_field = np.zeros_like(coords) * u.T
        for elem in cls.objects:
            mag_field = mag_field + elem.mag_field(coords)

        return mag_field
    @classmethod
    def time_step(cls, dt):
        for elem in cls.objects:
            elem.time_step(dt)

    @classmethod
    def draw(cls):
        for elem in cls.objects:
            elem.draw()

@dataclass
class Particle:
    mass: pint.Quantity # kg
    pos: pint.Quantity # m
    velocity: pint.Quantity = 0 * u.m/u.s # m/s
    charge: pint.Quantity = 0 * u.C # C


    def __post_init__(self):
        self.view_elem = gl.GLScatterPlotItem()
        view.addItem(self.view_elem)
        self.view_elem.setData(pos=self.pos)

    def elec_field(self, pos):
        dist = pos-self.pos
        r = np.linalg.norm(dist)
        if r <= small_dist:
            return np.zeros_like(pos) * u.V/u.m
        r_hat = dist/r
        return self.charge * k * r_hat/r**2

    def mag_field(self, pos):
        dist = pos-self.pos
        r = np.linalg.norm(dist)
        if r <= small_dist:
            return np.zeros_like(pos) * u.T
        r_hat = dist/r
        return self.charge * u_0/(4*pi) * (np.cross(self.velocity, r_hat)/r**2)
    
    def time_step(self, dt):
        force = self.charge*np.cross(self.velocity, World.mag_field(self.pos)) + self.charge * World.elec_field(self.pos)
        acceleration = force/self.mass
        self.velocity += acceleration * dt
        self.pos = self.pos + self.velocity * dt

        print(np.dot(particle.velocity, acceleration))


    def draw(self):
        self.view_elem.setData(pos=self.pos)

@dataclass
class UniformField:
    B: pint.Quantity = np.array([0, 0, 0])*u.tesla 
    E: pint.Quantity = np.array([0, 0, 0])*u.volt/u.meter # or Newton/Coulomb
    def mag_field(self, pos):
        return self.B
    def elec_field(self, pos):
        return self.E
    def time_step(self, dt):
        pass
    def draw(self):
        pass





view.clear()

scatterplot = gl.GLScatterPlotItem()

particle = Particle(1*u.kg, np.array([1, 0, 0])*u.m, 
                    velocity = np.array([1, 0, 0])*u.m/u.s, 
                    charge=1 *u.C)
uniform = UniformField(B=np.array([0, 0, 1])*u.tesla, E=np.array([0, 0, 1])*u.volt/u.meter)
World.add(particle)
World.add(uniform)


scatterplot.setData(pos=particle.pos)

grid = gl.GLGridItem()

view.addItem(grid)
view.addItem(scatterplot)

view.show()
dt = 0.01 * u.s

def render():
    # sleep(1)
    World.time_step(dt)
    World.draw()
    # print(np.sqrt(np.sum(particle.velocity**2)))
    

timer = QtCore.QTimer()
timer.timeout.connect(render)
timer.start(10)

if __name__ == '__main__':
    pg.exec()

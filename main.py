import numpy as np
import sys
from vispy import scene
from vispy.visuals.transforms import STTransform


class Sphere:
    def __init__(self, x=0.0, y=0.0, z=1.0, r=1.0):
        self.x, self.y, self.z, self.r = x, y, z, r

    def as_tuple(self):
        return self.x, self.y, self.z, self.r

    def to_barycentric(self):
        u = (2/3**0.5) * self.y
        v = self.x + (-1/3**0.5) * self.y
        return Sphere(u, v, self.r, self.r)

    def to_cartesian(self):
        x = 1/2 * (self.x / (self.x + self.y + self.z)) + (self.y / (self.x + self.y + self.z))
        y = (3**0.5/2) * (self.x / (self.x + self.y + self.z))
        return Sphere(x, y, self.r, self.r)

class Engine:
    def __init__(self, view):
        self.view = view
        self.spheres = set()

    def draw_barycentric(self, s: Sphere):
        s2 = s.to_cartesian()
        sphere1 = scene.visuals.Sphere(radius=s.r, method='ico', parent=self.view.scene,
                                       edge_color='black', color=(s.x / (s.x + s.y + s.z),
                                                                  s.y / (s.x + s.y + s.z),
                                                                  s.z / (s.x + s.y + s.z)))
        sphere1.transform = STTransform(translate=[s2.x, s2.y, s2.z])

    def draw_spheres(self):
        for s in self.spheres:
            e.draw_barycentric(s)

    def tangent_barycentric(self, s1: Sphere, s2: Sphere, s3: Sphere, cutoff: Sphere):
        s = Sphere(s1.x + s2.x + s3.x - cutoff.x, s1.y + s2.y + s3.y - cutoff.y, s1.z + s2.z + s3.z - cutoff.z, 0)
        if s.x < 0 or s.y < 0 or s.z < 0 or (s.x + s.y + s.z) == 0:
            return
        s.r = 1 / (s.x + s.y + s.z) / 2
        return s

    def dfs(self, depth, recdepth, s1: Sphere, s2: Sphere, s3: Sphere, cutoff: Sphere):
        next = self.tangent_barycentric(s1, s2, s3, cutoff)
        if not next or recdepth == 0 or next.r < depth:
            return
        self.spheres.add(next)
        self.dfs(depth, recdepth - 1, s1, s2, next, s3)
        self.dfs(depth, recdepth - 1, s1, next, s3, s2)
        self.dfs(depth, recdepth - 1, next, s2, s3, s1)


canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600), show=True)

view = canvas.central_widget.add_view()
view.camera = 'arcball'

e = Engine(view)
s1 = Sphere(1, 0, 0, 0.5)
s2 = Sphere(0, 1, 0, 0.5)
s3 = Sphere(0, 0, 1, 0.5)

mids = e.tangent_barycentric(s1, s2, s3, Sphere(0, 0, 0)).to_cartesian()
view.camera.set_range(x=[mids.x - 1, mids.x + 1], y=[mids.y - 1, mids.y + 1], z=[0, 1])

e.draw_barycentric(s1)
e.draw_barycentric(s2)
e.draw_barycentric(s3)

e.dfs(0.03, 8, s1, s2, s3, Sphere(0, 0, 0))
e.draw_spheres()

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()

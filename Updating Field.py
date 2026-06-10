import pyvista as pv
import time
import numpy as np

pl = pv.Plotter()

# mesh = pv.Sphere()

x, y, z = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
points = np.vstack((x.ravel(), y.ravel(), z.ravel())).T




u = np.ones_like(x)
v = np.zeros_like(u)
w = np.sin(x)
vectors = np.vstack((u.ravel() ** 3, v.ravel() ** 3, w.ravel() ** 3)).T
pdata = pv.vector_poly_data(points, vectors)
glyph = pdata.glyph(orient='vectors', scale='mag')

actor = pl.add_mesh(glyph)

pl.show(auto_close=False, interactive_update=True)

print(dir(actor))
vects = pdata["vectors"]

t = 0.0

for i in range(200):
    pdata["vectors"][:, 2] = np.sin(x.ravel() + t)

    # glyph = pdata.glyph(orient='vectors', scale='mag')
    new_glyph = pdata.glyph(orient="vectors", scale="mag")

    actor.mapper.dataset.copy_from(new_glyph)


    # actor.position = (i * 0.01, 0, 0)
    # pl.render()
    pl.update()
    t+=0.1
    time.sleep(0.01)


pl.close()
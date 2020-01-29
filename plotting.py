import matplotlib.pyplot as plt
from descartes import PolygonPatch
from . import colormap

def plot_polygon(poly, name = None):
    fig = plt.figure(figsize = (6, 6), dpi = 300)
    ax = fig.add_subplot(111)
    ax.axis("equal")
    ax.add_patch(PolygonPatch(poly))
    ax.autoscale()
    if name is not None:
        ax.set_title(name)
    plt.show()

def plot_polygons(polys, name = None, xlim=None, ylim=None, figsize = (12, 12), dpi = 300):
    colors = colormap.rescale_and_interpolate(colormap.turbo_colormap_data,
                                              range(0, len(polys)))
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)
    ax.axis("equal")
    for poly, color in zip(polys, colors):
        ax.add_patch(PolygonPatch(poly, facecolor = color, linewidth = 0.1))
    ax.autoscale()
    ax.set_title(name)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    plt.show()

def multiplot_polygons(polys, names = None, columns = 2, figsize = (12, 24), dpi = 300):
    if names is None:
        names = range(len(polys))
    colors = colormap.rescale_and_interpolate(colormap.turbo_colormap_data,
                                              range(0, len(polys)))
    fig = plt.figure(figsize=figsize, dpi=dpi)
    rows = len(polys) // columns
    if len(polys) % columns != 0:
        rows += 1
    for i, (poly, name, color) in enumerate(zip(polys, names, colors)):
        ax = fig.add_subplot(rows, columns, i + 1)
        ax.axis("equal")
        ax.add_patch(PolygonPatch(poly, facecolor = color, linewidth = 0.1))
        ax.autoscale()
        ax.set_title(name)
        ax.set_xticks([])
        ax.set_yticks([])
    plt.show()
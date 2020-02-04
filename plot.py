import matplotlib.pyplot as plt
from descartes import PolygonPatch
from . import colormap


def polygon(poly, name=None):
    fig = plt.figure(figsize=(6, 6), dpi=300)
    ax = fig.add_subplot(111)
    ax.axis("equal")
    ax.add_patch(PolygonPatch(poly))
    ax.autoscale()
    if name is not None:
        ax.set_title(name)
    plt.show()


def polygons(polys, name=None, xlim=None, ylim=None, figsize=(12, 12), dpi=300):
    colors = colormap.rescale_and_interpolate(
        colormap.turbo_colormap_data, range(0, len(polys))
    )
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)
    ax.axis("equal")
    for i, (poly, color) in enumerate(zip(polys, colors)):
        try:
            ax.add_patch(PolygonPatch(poly, facecolor=color, linewidth=0.1))
        except ValueError as e:
            continue
    ax.autoscale()
    ax.set_title(name)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    return fig


def polygon_subplots(polys, names=None, columns=2, figsize=(12, 24), dpi=300):
    if names is None:
        names = range(len(polys))
    colors = colormap.rescale_and_interpolate(
        colormap.turbo_colormap_data, range(0, len(polys))
    )
    fig = plt.figure(figsize=figsize, dpi=dpi)
    rows = len(polys) // columns
    if len(polys) % columns != 0:
        rows += 1
    for i, (poly, name, color) in enumerate(zip(polys, names, colors)):
        try:
            ax = fig.add_subplot(rows, columns, i + 1)
            ax.axis("equal")
            ax.add_patch(PolygonPatch(poly, facecolor=color, linewidth=0.1))
            ax.autoscale()
            ax.set_title(name)
            ax.set_xticks([])
            ax.set_yticks([])
        except ValueError as e:
            continue
    plt.show()


def points(x, y, name=None, xlim=None, ylim=None, figsize=(12, 12), dpi=300):
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)
    ax.axis("equal")
    ax.scatter(x, y)
    ax.autoscale()
    ax.set_title(name)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    plt.show()

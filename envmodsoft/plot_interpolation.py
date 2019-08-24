import copy
import os
import subprocess

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from osgeo import gdal

from pymica.pymica import PyMica


def crop_to_cat(inRaster):
    outRaster = './temporal_interpolation.tif' 
    subprocess.call(['gdalwarp', inRaster, outRaster, '-cutline',
                     '../envmodsoft/data/explanatory/cat_limits_shp/catalunya_fronteres.shp', 
                     '-dstnodata','-9999'])

    raster = gdal.Open(outRaster)
    ds = raster.ReadAsArray()
    os.remove(outRaster)

    return ds


def get_tif_array_crop(tifpath):
    ds = gdal.Open(tifpath)
    data = crop_to_cat(tifpath)
    gt = ds.GetGeoTransform()

    xres = gt[1]
    yres = gt[5]

    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5

    xx, yy = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]


    return xx, yy, data


def get_tif_array(tifpath, inEPSG, outEPSG):

    ds = gdal.Open(tifpath)
    data = ds.ReadAsArray()
    gt = ds.GetGeoTransform()

    xres = gt[1]
    yres = gt[5]

    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5

    xx, yy = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]

    return xx, yy, data


def plot_interpolation(tif_file, var):
    if var == 'temp':
        clevs = [-20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8,
                 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38,
                 40]
        cmap = plt.cm.colors.ListedColormap([[70/255, 68/255, 188/255],
                                             [120/255, 86/255, 216/255],
                                             [130/255, 103/255, 206/255],
                                             [140/255, 123/255, 198/255], 
                                             [151/255, 140/255, 186/255],
                                             [143/255, 73/255, 143/255],
                                             [163/255, 101/255, 163/255],
                                             [182/255, 129/255, 182/255],
                                             [204/255, 159/255, 204/255],
                                             [210/255, 176/255, 215/255],
                                             [226/255, 246/255, 247/255],
                                             [184/255, 238/255, 242/255],
                                             [163/255, 224/255, 226/255],
                                             [143/255, 209/255, 220/255],
                                             [114/255, 183/255, 194/255],
                                             [69/255, 167/255, 105/255],
                                             [71/255, 209/255, 102/255],
                                             [73/255, 248/255, 117/255],
                                             [154/255, 233/255, 154/255],
                                             [208/255, 245/255, 172/255],
                                             [237/255, 238/255, 165/255],
                                             [242/255, 218/255, 145/255],
                                             [243/255, 172/255, 96/255],
                                             [243/255, 150/255, 75/255],
                                             [255/255, 147/255, 147/255],
                                             [242/255, 110/255, 110/255],
                                             [255/255, 63/255, 63/255],
                                             [201/255, 86/255, 86/255],
                                             [180/255, 65/255, 65/255],
                                             [184/255, 63/255, 63/255]])

    field = get_tif_array_crop(tif_file)

    fig, ax = plt.subplots(figsize=(10, 10))

    im = ax.contourf(field[0], field[1], field[2][:, :].T, clevs, cmap=cmap)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.ax.tick_params(labelsize=10, width=0.5, length=2.2, pad=2)

    if var == 'temp':
        cbar.set_label('Air temperature (\u00b0C)', size=10)
    cbar.outline.set_linewidth(0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.show()

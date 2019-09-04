import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from osgeo import gdal
import subprocess
import os
import geopandas as gp


def crop_to_cat(inRaster):
    outRaster = './temporal_interpolation.tif' 
    subprocess.call(['gdalwarp', inRaster, outRaster, '-cutline',
                     'envmodsoft/data/explanatory/cat_limits_shp/catalunya_fronteres.shp', 
                     '-dstnodata','-9999'])

    raster = gdal.Open(outRaster)
    ds = raster.ReadAsArray()
    os.remove(outRaster)

    return ds


def get_tif_array_crop(tifpath):
    ds = gdal.Open(tifpath)
    data = crop_to_cat(tifpath)
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()

    xres = gt[1]
    yres = gt[5]

    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5

    xx, yy = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]


    return xx, yy, data

fig = plt.figure(figsize=(2.85,2.85), frameon=False)
ax1 = plt.subplot()

levels = np.arange(0, 1.2, 0.2)

d_coast = get_tif_array_crop('envmodsoft/data/explanatory/' +
                             'cat_distance_coast.tif')
d_coast[2][d_coast[2] < -1] = np.nan

im1 = ax1.contourf(d_coast[0], d_coast[1], d_coast[2][:, :].T, levels=levels,
                   cmap=plt.cm.get_cmap('YlGnBu_r'))
ax1.set_aspect('equal')
ax1.axis('off')

cbar_ax = fig.add_axes([0.45, 0.20, 0.30, 0.015])
cbar = plt.colorbar(im1, cax=cbar_ax, orientation='horizontal', ticks=levels)
cbar.ax.tick_params(labelsize=3.5, width=0.3, size=2, pad=1)
cbar.outline.set_linewidth(0.3)
cbar.set_label('Distance to coast function', size=4)#(\u00b0C)', size=8)

plt.savefig('/tmp/ems_distance_coast.pdf', bbox_inches='tight', pad=0)

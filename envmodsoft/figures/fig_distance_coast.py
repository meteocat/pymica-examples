import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from osgeo import gdal
import subprocess
import os
import geopandas as gp
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


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

cbar_ax = fig.add_axes([0.35, 0.16, 0.30, 0.015])
cbar = plt.colorbar(im1, cax=cbar_ax, orientation='horizontal', ticks=levels)
cbar.ax.tick_params(labelsize=3.5, width=0.3, size=2, pad=1)
cbar.outline.set_linewidth(0.3)
cbar.set_label('Distance to coast function', size=4)#(\u00b0C)', size=8)


coast_line = gp.read_file('sample-data/explanatory/cat_coast_line.json')
coast_line.plot(ax=ax1, color='red', linewidth=0.8, label='Coast line')
ax1.legend(loc='lower right', fontsize=4, frameon=False)
ax1.text(271030, 4742408, 'a)', size=5)

mbaxes = inset_axes(ax1, width="100%", height="100%",
                    bbox_to_anchor=[430000,4510040,120000,60000],
                    bbox_transform=ax1.transData, loc='lower left')
mbaxes.spines['bottom'].set_linewidth(0.1)
mbaxes.spines['top'].set_linewidth(0.1)
mbaxes.spines['right'].set_linewidth(0.1)
mbaxes.spines['left'].set_linewidth(0.1)

world = gp.read_file('envmodsoft/data/explanatory/world_boundaries.geojson')
ax2 = world.plot(ax=mbaxes, facecolor='None', edgecolor='darkgrey', linewidth=0.3)
ax2.set_xlim(-4, 15)
ax2.set_ylim(36, 48)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.text(-6.0, 46.8, 'b)', size=5)

catalonia = gp.read_file('envmodsoft/data/explanatory/cat_boundaries.geojson')
catalonia.plot(ax=mbaxes, facecolor='darkgrey', edgecolor='None')

ax1.set_xlim(260000, 530000)
ax1.set_ylim(4488100, 4750000)

plt.savefig('/tmp/ems_distance_coast.pdf', pad=0)

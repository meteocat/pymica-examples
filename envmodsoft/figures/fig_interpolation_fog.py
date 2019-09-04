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


gs = gridspec.GridSpec(1, 2)
fig = plt.figure(figsize=(5,2.85), frameon=False)
ax1 = plt.subplot(gs[0,0])
ax2 = plt.subplot(gs[0,1])

int_global = get_tif_array_crop('envmodsoft/output/' +
                                'tair_20181231_1400_noclusters.tif')
im1 = ax1.contourf(int_global[0], int_global[1], int_global[2][:, :].T, clevs,
                   cmap=cmap)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.text(271030, 4742408, 'a)', size=3)


clusters_6 = gp.read_file('envmodsoft/clusters/clusters-6-clipped.geojson')

int_clusters = get_tif_array_crop('envmodsoft/output/' +
                                  'tair_20181231_1400_clusters.tif')
ax2.contourf(int_clusters[0], int_clusters[1], int_clusters[2][:, :].T, clevs,
             cmap=cmap)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.text(271030, 4742408, 'b)', size=3)

clusters_6.plot(ax=ax2, facecolor='None', edgecolor='black', linewidth=0.3)

cbar_ax = fig.add_axes([0.35, 0.15, 0.30, 0.015])
cbar = plt.colorbar(im1, cax=cbar_ax, orientation='horizontal')
cbar.ax.tick_params(labelsize=3, width=0.3, size=2, pad=1)
cbar.outline.set_linewidth(0.3)
cbar.set_label('Air temperature (\u00b0C)', size=3)#(\u00b0C)', size=8)


plt.savefig('/tmp/ems_interpolation_comparison.pdf', bbox_inches='tight', pad=0)

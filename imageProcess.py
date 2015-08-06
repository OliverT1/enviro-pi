# Written by Oliver Turnbull for EnviroPi project, part of the AstroPi competition

from PIL import Image
import numpy
import sys
import time
import matplotlib
from matplotlib import pyplot as plt
startTime = time.time()


    
def convertImage(directory):
    
    # Opens image to be converted
    img = Image.open('raw/%s' %directory)
    # Places red and blue values in numpy arrays
    imgR, imgG, imgB = img.split() #get channels
    
    # Places red and blue values in numpy arrays
    arrR = numpy.asarray(imgR).astype('float32')
    arrB = numpy.asarray(imgB).astype('float32')
    
    # Calculates the NDVI value by dividing
    # Red minus Blue over Red plus Blue
    num = (arrR - arrB)
    denom = (arrR + arrB)
    arrNdvi = num/denom

    AUTO_CONTRAST = False
    
    # Changes colour map, jet has been used
    customCmap= plt.set_cmap('jet')
    img_w, img_h = img.size
    
 
    
    dpi   = 600#int(img_w/fig_w)
    vmin  = -1 #most negative NDVI value
    vmax  = 1 #most positive NDVI value
    if AUTO_CONTRAST:
       vmin = arrNdvi.min()
       vmax = arrNdvi.max()

    #lay out the plot, making room for a colorbar space
    fig_w = img_w/dpi
    fig_h = img_h/dpi
    fig = plt.figure(figsize=(fig_w,fig_h), dpi=dpi)
    fig.set_frameon(False)

    #make an axis for the image filling the whole figure except colorbar space
    ax_rect = [0.0, #left
               0.0, #bottom
               1.0, #width
               1.0] #height
    ax = fig.add_axes(ax_rect)
    ax.yaxis.set_ticklabels([])
    ax.xaxis.set_ticklabels([])
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

    axes_img = ax.imshow(arrNdvi,
                          cmap = customCmap,
                          vmin = vmin,
                          vmax = vmax,
                          aspect = 'equal',
                         )
    
    # Adds colorbar, used for illustritive purposes but turned off for actual EnviroPi experiment
    #cax = fig.add_axes([0.95, 0.05, 0.025, 0.90] )
    #cbar = fig.colorbar(axes_img, cax=cax)
    
    #fig.tight_layout(pad=0)
    fig.savefig("ProcessedImages/%s" % directory,
                dpi=dpi,
                bbox_inches='tight',
                pad_inches=0.0,
               )
    
    plt.close(fig)
    return numpy.mean(arrNdvi, )


# Reads in files from cmd prompt
for line in sys.stdin:
    # Removes new line character
    line = line.rstrip('\n')
    print (line)
    newNDVI = convertImage(line)
    
# How long taken to compute images
print('time taken %s seconds' %(time.time() - startTime))

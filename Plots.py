import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from scipy import ndimage
import time


def PlotCFAR(data,labels = {
    "x_label":"Velocity [knots]",
    "y_label":"Range [m]",
    "title": "CFAR"

},isoAxis = True, rotation = True):


    
    plt.figure(figsize=(10,10))

    if rotation > 0:
        rotated_img = np.rot90(data)
    else:

        rotated_img = data 

    plt.imshow(rotated_img)
    if isoAxis:
        plt.yticks(np.linspace(0,256,9),labels=np.round(np.linspace(255*0.785277,0,9)),size =15)
        plt.xticks(np.linspace(0,256,7),labels=np.round(np.linspace(-0.127552440715*127,0.127552440715*127,7),2),size =15)
    

    plt.xlabel(labels["x_label"],fontdict = {'fontsize' : 20})
    plt.ylabel(labels["y_label"],fontdict = {'fontsize' : 20})
    plt.title(labels["title"],fontdict = {'fontsize' : 30})
    plt.grid(False)
    plt.savefig(f"plots/CFAR_{time.time_ns()}.png")
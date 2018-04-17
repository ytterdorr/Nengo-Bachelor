#Setup the environment
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline

import nengo
from nengo.utils.matplotlib import rasterplot

model = nengo.Network(label='A Single Neuron')
with model:
    #Input
    cos = nengo.Node(lambda t: np.cos(16 * t))
    
    #Ensemble with one neuron
    neuron = nengo.Ensemble(1, dimensions=1,  # Represent a scalar
                            encoders=[[1]])   # Sets the neurons firing rate to increase for positive input
    
    #Connecting input to ensemble
    nengo.Connection(cos, neuron)

from nengo_gui.ipython import IPythonViz
IPythonViz(model, "singleneuron.py.cfg")

from IPython.display import Image
Image(filename='singleneuron.png')


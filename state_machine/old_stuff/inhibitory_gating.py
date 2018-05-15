import numpy as np
import matplotlib.pyplot as plt

import nengo

# 1 Create the network

n_neurons = 30
model = nengo.Network(label="Inhibitory Gating")
with model:
	A = nengo.Ensemble(n_neurons, dimensions=1)
	B = nengo.Ensemble(n_neurons, dimensions=1)
	C = nengo.Ensemble(n_neurons, dimensions=1)

# 2 Privide the input to the model
from nengo.processes import Piecewise

with model:
	sin = nengo.Node(np.sin)
	inhib = nengo.Node(Piecewse({0: 0, 2.5: 1, 5: 0, 7.5: 1, 10: 0, 12.5: 1}))

# 3 Connect the different components of the model
with model:
	nengo.Connection(sin, A)
	nengo.Connection(sin, B)
	nengo.Connection(inhib, A.neurons, transform=[[-2.5]]*n_neurons)
	nengo.Connection(inhib, C)
	nengo.Connection(C, B.neurons, transform=[[-2.5]] * n_neurons)


# 4 Probe outputs
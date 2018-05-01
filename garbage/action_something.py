#action_test.
# Found this somewhere where python examples were
# https://github.com/nengo/nengo/blob/master/examples/networks/basal_ganglia.ipynb
import numpy as np
import matplotlib.pyplot as plt

import nengo



model = nengo.Network(label='Basal Ganglia')
with model:
    basal_ganglia = nengo.networks.BasalGanglia(dimensions=3)


class ActionIterator(object):
    def __init__(self, dimensions):
        self.actions = np.ones(dimensions) * 0.1

    def step(self, t):
        # one action at time dominates
        dominate = int(t % 3)
        self.actions[:] = 0.1
        self.actions[dominate] = 0.8
        return self.actions


action_iterator = ActionIterator(dimensions=3)

with model:
    actions = nengo.Node(action_iterator.step, label="actions")


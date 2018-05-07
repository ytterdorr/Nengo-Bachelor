import nengo
import numpy as np
import time

"""
class TurnState(nengo.Node):

    def __init__(self, size_in=1):
        self.turn_start = 0
        super(TurnState, self).__init__(self.update)

    def turn(self):
        time.sleep(1)

    def update(t, start_signal):
        if start_signal > 0.9:
            self.turn()
"""

def turn_function(t, start_signal):
    if start_signal > 0.9:
        return 1
    else:
        return 0
model = nengo.Network()
with model:
    turn_node = nengo.Node(turn_function, size_in=1)
    turn_input = nengo.Node(0)
    turn_neurons = nengo.Ensemble(n_neurons=20, dimensions=1)

    nengo.Connection(turn_input, turn_neurons)
    nengo.Connection(turn_neurons, turn_node)
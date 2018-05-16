import numpy as np
import nengo
import nengo.spa as spa
import grid
import math

map = '''
#########
#       #
#       #
#       #
#       #
#       #
#       #
#       #
#########
'''

# this defines the world the agent is in, based on the map above
class Cell(grid.Cell):
    def load(self, c):
        if c == '#':
            self.wall = True
    
    def color(self):
        if self.wall:
            return 'black'

# this is for creating a new type of object in the environment            
class Food(grid.ContinuousAgent):
    color = 'green'
    shape = 'circle'
            
# now we actuall make the world
world = grid.World(Cell, map=map, directions=4)
body = grid.ContinuousAgent()
world.add(body, x=2, y=2, dir=1) 



    
def starter(t):
    if t < 0.1:
        return "START"
    else:
        return "0"

def get_body_angle(t):
    angle = (body.dir-1) * 2 * np.pi / 4
    return angle

def get_body_angle2():
    angle = (body.dir-1) * 2 * np.pi / 4
    return angle

# Get a start angle
turn_start = get_body_angle2()

def angle_diff_exceeded(t, action):
    # For a feedback node
    turn = vocab.parse("TURN").v
    # Check if in TURN state
    if np.dot(action, turn) > 0.9:
        if abs(get_body_angle2() - turn_start) > 0.8:
            return vocab.parse("STOP").v
        else:
            return vocab.parse("TURN").v
    else:
        return vocab.parse("0").v

def turn_function(t, x):
    return body.turn(x*0.003)

dimensions = 32
vocab = spa.Vocabulary(dimensions)
model = spa.SPA()



with model:

    def check_turn(t, action):
        turn = vocab.parse("TURN").v
        if np.dot(action, turn) > 0.9:
            return 1
        else:
            return 0

    
    # Environment
    env = grid.GridNode(world)

    # Nodes
    body_turn = nengo.Node(lambda t, x: body.turn(x*0.003), size_in=1)
    turn_checker = nengo.Node(check_turn, size_in=dimensions)
    feedback_node = nengo.Node(angle_diff_exceeded, size_in=dimensions)
    


    # State
    model.action_state = spa.State(dimensions, vocab=vocab, feedback=1, feedback_synapse=0.01)
    
    actions = spa.Actions(
        'dot(action_state, START) --> action_state=TURN',
        #'dot(action_state, TURN) --> action_state=WAIT',
        )

    model.bg = spa.BasalGanglia(actions=actions)
    model.thal = spa.Thalamus(model.bg)

    # Connections
    nengo.Connection(model.action_state.output, turn_checker)
    nengo.Connection(model.action_state.output, feedback_node)
    nengo.Connection(feedback_node, model.action_state.input)
    nengo.Connection(turn_checker, body_turn)

    model.start_input = spa.Input(action_state=starter)
        
    #turn_tracker = TurnNode(body, size_in=1)
    # Tracking the direction of the body object
    #angle_node = nengo.Node(get_body_angle)

    #angle_gate = nengo.Network()
    #with angle_gate:
    #    turn_unput = 
    #angle_keeper = nengo.Ensemble(n_neurons=50, dimensions=1)

    #nengo.Connection(turn_checker, turn_tracker)
    #nengo.Connection(angle_node, angle_gate[0])
    #nengo.Connection(turn_checker, angle_gate[1])
    #nengo.Connection(angle_gate, angle_gate[2], function=gating)
    #nengo.Connection(angle_gate, angle_keeper, function=gating, synapse=0.01)
"""
class TurnNode(nengo.Node):

    def __init__(self, body, size_in):
        self.body = body
        self.angle = self.get_body_angle()
        super(TurnNode, self).__init__(self.update, size_in=size_in)

    def get_body_angle(self):
        angle = (body.dir-1) * 2 * np.pi / 4
        return angle

    def update(self, t):
        return 1


def gating(x):
        # channel 0: body angle
        # channel 1: turn_checker
        # channel 2: own output
        if x[1] > 0.6:
            return x[2]
        else:
            return x[0]

"""
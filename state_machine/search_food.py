import nengo
import nengo.spa as spa
import numpy as np
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

D = 32
vocab = spa.Vocabulary(D)
model = spa.SPA(label="SearchFood")


def food_input(t):
    if t < 1:
        return "NOFOOD"
    else:
        return "FOOD"

def starter(t):
    if t < 0.1:
        return "START"
    else:
        return "0"

def check_turn(t, action):
    turn = vocab.parse("TURN").v
    if np.dot(action, turn) > 0.5:
        return 1
    else:
        return 0

def check_forward(t, action):
    forward = vocab.parse("FORWARD").v
    if np.dot(action, forward) > 0.5:
        return 1
    else:
        return 0


def turn_function(t, x):
    return body.turn(x*0.003)

def forward_function(t, x):
    return body.go_forward(x*0.01)

        
with model:

    # Environment
    env = grid.GridNode(world)
    
    model.subgoal = spa.State(D)
    model.action_state = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)
    model.food_percept = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)
    model.food_state = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)


    actions = spa.Actions(
        'dot(action_state, START*0.6) -2*dot(food_percept, FOOD) --> action_state=CHECK1, food_percept=food_state',
        'dot(action_state, CHECK1*0.6) -2*dot(food_percept, FOOD) --> action_state=TURN',
        'dot(action_state, TURN*0.6) -2*dot(food_percept, FOOD) --> action_state=CHECK2',
        'dot(action_state, CHECK2*0.6) -2*dot(food_percept, FOOD) --> action_state=FORWARD, food_percept=food_state',
        'dot(action_state, FORWARD*0.6) -2*dot(food_percept, FOOD) --> action_state=CHECK1',
        'dot(food_percept, FOOD) --> action_state=STOP, subgoal=SEEK_FOOD',
        '0.5 --> ',
        )

    model.bg = spa.BasalGanglia(actions=actions)
    model.thal = spa.Thalamus(model.bg)

    ## Inputs and outputs
    model.food_input = spa.Input(food_state=food_input)
    model.start_input = spa.Input(action_state=starter)

    # Turning
    check_turn_node = nengo.Node(check_turn, size_in=D)
    turn_node = nengo.Node(turn_function, size_in=1)
    nengo.Connection(model.action_state.output, check_turn_node)
    nengo.Connection(check_turn_node, turn_node)

    # Going forward
    check_forward_node = nengo.Node(check_forward, size_in=D)
    forward_node = nengo.Node(forward_function, size_in=1)
    nengo.Connection(model.action_state.output, check_forward_node)
    nengo.Connection(check_forward_node, forward_node)

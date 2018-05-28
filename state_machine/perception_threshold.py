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
world.add(body, x=2, y=4, dir=1) 
world.add(Food(), x=5, y=2)
#world.add(Food(), x=3, y=6)

D = 32
vocab = spa.Vocabulary(D)
model = spa.SPA(label="SearchFood")


class State(nengo.Node):
    def __init__(self, body):
        self.body = body
        super(State, self).__init__(self.update)
        
        
    def compute_angle_and_distance(self, obj):
        angle = (body.dir-1) * 2 * np.pi / 4
        dy = obj.y - self.body.y
        dx = obj.x - self.body.x
        obj_angle = np.arctan2(dy, dx)
        theta = angle - obj_angle
        dist = np.sqrt(dy**2 + dx**2)
        return theta, dist

    def update(self, t):
        where = []
        what = []
        color_map = dict(green=1, red=-1)
        self.n_objects = 0
        self.percept_thresh = 3
        for obj in world.agents:
            if obj is not self.body:
                angle, dist = self.compute_angle_and_distance(obj)
                color = color_map[obj.color]
                ball_type = 0 # none

                if dist < 1:
                    dist = 1.0
                
                if dist > self.percept_thresh:
                    # Make the ball irrelevant.
                    dist = 100
                    ball_type = 0
                else:
                    ball_type = color

                r = 1.0/dist
                where.extend([np.sin(angle)*r, np.cos(angle)*r])
                what.extend([ball_type])
                self.n_objects += 1

        return what+where      


with model:

    ### Environment
    env = grid.GridNode(world)

    ### Perceptions
    sensors = State(body)
    what = nengo.networks.EnsembleArray(n_ensembles=sensors.n_objects,
                                        ens_dimensions=1,
                                        n_neurons=50)
    where = nengo.networks.EnsembleArray(n_ensembles=sensors.n_objects,
                                         ens_dimensions=2,
                                         n_neurons=100,
                                         intercepts=nengo.dists.Uniform(0.1, 1.0))
    nengo.Connection(sensors[:sensors.n_objects], what.input, synapse=None)
    nengo.Connection(sensors[sensors.n_objects:], where.input, synapse=None)
    
    ### SPA State machine
    model.subgoal = spa.State(D)
    model.action_state = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)
    model.food_percept = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)
    model.food_state = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)


    actions = spa.Actions(
        'dot(action_state, START*0.6) -2*dot(food_percept, FOOD) --> action_state=CHECK1',
        'dot(action_state, CHECK1*0.6) -2*dot(food_percept, FOOD) --> food_percept=food_state, action_state=WAIT1',
        'dot(action_state, WAIT1*0.6) -2*dot(food_percept, FOOD) --> action_state=TURN',
        'dot(action_state, TURN*0.6) -2*dot(food_percept, FOOD) --> action_state=CHECK2',
        'dot(action_state, CHECK2*0.6) -2*dot(food_percept, FOOD) --> food_percept=food_state, action_state=WAIT2',
        'dot(action_state, WAIT2*0.6) -2*dot(food_percept, FOOD) --> action_state=FORWARD',
        'dot(action_state, FORWARD*0.6) -2*dot(food_percept, FOOD) --> action_state=CHECK1',
        'dot(food_percept, FOOD) --> action_state=STOP, subgoal=SEEK_FOOD',
        #'0.5 --> action_state=START',
        )

    model.bg = spa.BasalGanglia(actions=actions)
    model.thal = spa.Thalamus(model.bg)

    ### Start signal
    def starter(t):
        if t < 0.05:
            return "START"
        else:
            return "0"
    
    model.start_input = spa.Input(action_state=starter)

    
    ### Turning
    
    def check_turn(t, action):
        turn = vocab.parse("TURN").v
        if np.dot(action, turn) > 0.5:
            return 1
        else:
            return 0

    def turn_function(t, x):
        return body.turn(x[0]*x[1]*0.01)

    # Terry's turn towards function
    def turn_towards(x):
        if x[0] < -0.1:
            return 1
        elif x[0] > 0.1:
            return -1
        else:
            return 0
    
    check_turn_node = nengo.Node(check_turn, size_in=D)
    turn_ensemble = nengo.Ensemble(n_neurons=200, dimensions=2)
    turn_node = nengo.Node(turn_function, size_in=2)

    # How does this give a contionuous value?
    for i in range(sensors.n_objects):
        nengo.Connection(where.ensembles[i], turn_ensemble[1], function=turn_towards)
    
    nengo.Connection(model.action_state.output, check_turn_node)
    nengo.Connection(check_turn_node, turn_ensemble[0])
    nengo.Connection(turn_ensemble, turn_node)



    ### Going forward

    def check_forward(t, action):
        forward = vocab.parse("FORWARD").v
        if np.dot(action, forward) > 0.5:
            return 1
        else:
            return 0

    def forward_function(t, x):
        return body.go_forward(x*0.01)

    check_forward_node = nengo.Node(check_forward, size_in=D)
    forward_node = nengo.Node(forward_function, size_in=1)
    nengo.Connection(model.action_state.output, check_forward_node)
    nengo.Connection(check_forward_node, forward_node)

    
    ### Controlling the food input

    def get_r(sinCosArray):
        sin = sinCosArray[0]
        cos = sinCosArray[1]
        r = np.sqrt(sin*sin+cos*cos)
        return r
    
    def stop_if_r_is_large(sinCosArray):
        r_size = get_r(sinCosArray)
        if r_size > 0.9:
            return 1
        else:
            return 0

    def translate_food_state(t, food_is_close):
        food = vocab.parse("FOOD").v
        nofood = vocab.parse("NOFOOD").v
        
        if food_is_close > 0.5:
            return food
        else:
            return nofood

    close_to_food = nengo.Ensemble(n_neurons=50, dimensions=1)
    # node to send food state vector based on close_to_food ensemble output 
    food_node = nengo.Node(translate_food_state, size_in=1) 
    
    # How does this give a continuous value?
    for i in range(len(where.ensembles)):
        nengo.Connection(where.ensembles[i], close_to_food, function=stop_if_r_is_large)
    
    nengo.Connection(close_to_food, food_node)
    nengo.Connection(food_node, model.food_state.input)
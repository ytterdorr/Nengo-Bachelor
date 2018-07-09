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
        for obj in world.agents:
            if obj is not self.body:
                angle, dist = self.compute_angle_and_distance(obj)
                color = color_map[obj.color]
                
                if dist < 1:
                    dist = 1.0
                    
                r = 1.0/dist
                where.extend([np.sin(angle)*r, np.cos(angle)*r])
                what.extend([color])
                self.n_objects += 1
        return what+where        

    
D = 64
dim = 16
vocab = spa.Vocabulary(D)
food_vocab = spa.Vocabulary(D)
goal_vocab = spa.Vocabulary(D)
inter_vocab = spa.Vocabulary(D)
turn_vocab = spa.Vocab(dim)

model = spa.SPA(label="Find Food")

with model:

    def starter(t):
        if t < 0.05:
            return "START_FIND_FOOD"
        else:
            return "0"

    def food_exist_func(t):
        if t < 0.5:
            return "NO_FOOD"
        else:
            return "FOOD"

    def food_close_func(t):
        if t < 1:
            return "NO_FOOD"
        else:
            return "CLOSE"

    def interrupt_input(t):
        if t < 0.3:
            return "0"
        elif t < 0.4:
            return "INTERRUPT"
        else: 
            return "0"

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

    model.find_state = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.01)
    model.go_state = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.01)
    model.perception = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.05)
    model.subgoal = spa.State(dimensions=D, vocab=goal_vocab, feedback=1, feedback_synapse=0.01)
    model.subgoal_temp = spa.State(dimensions=D, vocab=goal_vocab, feedback=1, feedback_synapse=0.01)
    model.food_exists = spa.State(dimensions=D, vocab=vocab)
    model.food_close = spa.State(dimensions=D, vocab=vocab)
    model.interrupt = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.01)

    actions = spa.Actions(
        # What is the stop condition?
        ### FIND FOOD 
        'dot(subgoal, START_FIND_FOOD) --> find_state=START, subgoal=FIND_FOOD, go_state=STOP, subgoal_temp=START_FIND_FOOD',
        'dot(find_state, START) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> find_state=CHECK1',
        'dot(find_state, CHECK1) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> perception=food_exists, find_state=WAIT1',
        'dot(find_state, WAIT1) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> find_state=TURN',
        'dot(find_state, TURN) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> find_state=CHECK2',
        'dot(find_state, CHECK2) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> perception=food_exists, find_state=WAIT2',
        'dot(find_state, WAIT2) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> find_state=FORWARD',
        'dot(find_state, FORWARD) - dot(perception, FOOD) -2*dot(interrupt, INTERRUPT) --> find_state=CHECK1',
        # Stop condition
        'dot(perception, FOOD) --> find_state=STOP, subgoal=START_GO_TO_FOOD, subgoal_temp=START_GO_TO_FOOD',
        ### GO TO FOOD
        'dot(subgoal, START_GO_TO_FOOD) --> go_state=START, subgoal=GO_TO_FOOD, find_state=STOP, subgoal_temp=START_GO_TO_FOOD',
        'dot(go_state, START) --> go_state=CHECK1',
        'dot(go_state, CHECK1) --> go_state=WAIT1, perception=food_close',
        'dot(go_state, WAIT1) - dot(perception, CLOSE) --> go_state=TURN',
        'dot(go_state, TURN) - dot(perception, CLOSE) --> go_state=FORWARD',
        'dot(go_state, FORWARD) - dot(perception, CLOSE) --> go_state=CHECK1',
        # Stop condition
        'dot(perception, CLOSE) --> go_state=STOP',
        ### Interrupt
        'dot(interrupt, INTERRUPT) --> go_state=STOP, find_state=STOP, interrupt=CALC_TURN',
        'dot(interrupt, CALC_TURN) --> interrupt=TURN1',
        'dot(interrupt, TURN1) --> interrupt=TURN2',
        'dot(interrupt, TURN2) --> interrupt=TURN3',
        'dot(interrupt, TURN3) --> interrupt=FORWARD',
        'dot(interrupt, FORWARD) --> interrupt=STOP, subgoal=subgoal_temp',

        ) 
    model.bg = spa.BasalGanglia(actions=actions)
    model.thal = spa.Thalamus(model.bg)

    # Input
    model.start_input = spa.Input(subgoal=starter)
    model.exists_input = spa.Input(food_exists=food_exist_func)
    model.food_close_input = spa.Input(food_close=food_close_func)
    model.interrupt_input = spa.Input(interrupt=interrupt_input)

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
    
    #nengo.Connection(model.turn.output, check_turn_node)
    #nengo.Connection(check_turn_node, turn_ensemble[0])
    #nengo.Connection(turn_ensemble, turn_node)

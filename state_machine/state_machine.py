import numpy as np
import nengo
import nengo.spa as spa
import grid

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


# now we actuall make the world
world = grid.World(Cell, map=map, directions=4)
body = grid.ContinuousAgent()
world.add(body, x=2, y=2, dir=1)    # create the body for the agent

class WorldState(nengo.Node):
    def __init__(self, body):
        self.body = body
        super(WorldState, self).__init__(self.update)
        
    def compute_angle_and_distance(self, obj):
        angle = (body.dir-1) * 2 * np.pi / 4
        dy = obj.y - self.body.y
        dx = obj.x - self.body.x
        obj_angle = np.arctan2(dy, dx)
        theta = angle - obj_angle
        dist = np.sqrt(dy**2 + dx**2)
        return theta, dist

dimensions = 32

model = spa.SPA()
with model:
    food_substate = nengo.Node(0)
     
    def set_substate(substate):
        substate = (substate+1)%3
        return substate
    
    
    #model.goal = spa.State(dimensions)
    model.perception = spa.State(dimensions)
    model.goal = spa.State(dimensions, feedback=1, feedback_synapse=0.01)
    model.subgoal = spa.State(dimensions)
    actions = spa.Actions(
        'dot(perception, HUNGRY) --> goal=FOOD',
        'dot(perception, HEALTH_LOW) --> goal=HOME',
        'dot(perception, THREAT) --> goal=AVOID',
        'dot(perception, NONE) --> goal=SLEEP',
        'dot(perception, HUNGRY) --> food_substate = 2',
        )
    
    model.now_state = spa.State(dimensions)
    cortical_actions = spa.Actions(
        'now_state = goal*subgoal'
        )
        
    model.cortical = soa.cortical(cortical_actions)
    
    
    
    model.bg = spa.BasalGanglia(actions)
    model.thalamus = spa.Thalamus(model.bg)
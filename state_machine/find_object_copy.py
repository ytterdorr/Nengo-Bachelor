import numpy as np
import nengo
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

# this is for creating a new type of object in the environment            
class Food(grid.ContinuousAgent):
    color = 'green'
    shape = 'circle'
            
# now we actuall make the world
world = grid.World(Cell, map=map, directions=4)
body = grid.ContinuousAgent()
world.add(body, x=2, y=2, dir=1)    # create the body for the agent

world.add(Food(), x=2, y=4)         # create the other objects in the world
world.add(Food(), x=4, y=4)


# this is the sensory system.  It takes objects from the environment and
#  figures out where they are, returning the result as a vector that nengo
#  can then use.
#
# The sensory information is divided into "what" (information about what the
#  object is -- which in this case is just its color) and "where" (information
#  about the location of the object -- which in this case is cos(theta)/dist and
#  sin(theta)/dist).  Note that we're dividing by distance, so a large value means
#  that the object is very close, and a small value means it is far away)
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

# now we actually build the nengo model.
model = nengo.Network()
with model:
    # create a display for the world
    env = grid.GridNode(world)
    
    # create motor neurons and motor outputs for turning and going forward
    body_speed = nengo.Node(lambda t, x: body.go_forward(x[0]*0.01), size_in=1)
    body_turn = nengo.Node(lambda t, x: body.turn(x[0]*0.003), size_in=1)
    turn = nengo.Ensemble(n_neurons=50, dimensions=1)
    speed = nengo.Ensemble(n_neurons=50, dimensions=1)
    nengo.Connection(speed, body_speed)
    nengo.Connection(turn, body_turn)
    
    # create sensors and neurons to hold the sensors.  We are using an 
    #  EnsembleArray so that there are separate neurons to store the information
    #  for each object.
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
    

    
    # Now let's implement the simplest possible behaviour: turn towards objects.
    def turn_towards(x):
        if x[0] < -0.1:
            return 1
        elif x[0] > 0.1:
            return -1
        else:
            return 0
    # do the above function for all the objects
    for i in range(sensors.n_objects):
        nengo.Connection(where.ensembles[i], turn, function=turn_towards)

    def printer(t, sinCosArray):
        printer._nengo_html_ = "<p>Some Data:\n"+str(sinCosArray)+"</p>"
        ball_size = find_distance(sinCosArray)
        printer._nengo_html_ += "<p>Distance: "+str(ball_size)+"</p>"

    def find_distance(sinCosArray):
        sin = sinCosArray[0]
        cos = sinCosArray[1]
        r = np.sqrt(sin*sin+cos*cos)
        return r
        
    def stop_if_r_is_large(sinCosArray):
        size = find_distance(sinCosArray)
        if size > 0.95:
            return 1
        else:
            return 0
        
    def stop_speed(x):
        if x > 0.5:
            return -0.3
        else:
            return 0
    
    # TODO Make a display node
    display = nengo.Node(printer, size_in=2)
    nengo.Connection(where.ensembles[0], display)
    #nengo.Connection(where.ensembles[1], display)
    
    # Stop node
    stop = nengo.Ensemble(n_neurons=50, dimensions=1)
    for i in range(len(where.ensembles)):
        nengo.Connection(where.ensembles[i], stop, function=stop_if_r_is_large)
    nengo.Connection(stop, speed, function=stop_speed)   
    
    
    
    # and let's just move forward at a fixed speed.
    fixed_speed = nengo.Node(0.3)
    nengo.Connection(fixed_speed, speed)
    
    
    
    

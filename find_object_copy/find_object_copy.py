import numpy as np
import nengo
import grid

map = '''
##########
#        #
#        #
#        #
#        #
#        #
#        #
#        #
##########
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
    
class Threat(grid.ContinuousAgent):
    color = 'red'
    shape = 'circle'
            
# now we actuall make the world
world = grid.World(Cell, map=map, directions=4)
body = grid.ContinuousAgent()
world.add(body, x=2, y=2, dir=1)    # create the body for the agent

world.add(Food(), x=2, y=4)         # create the other objects in the world
#world.add(Threat(), x=4, y=4)
#world.add(Food(), x=6, y=2)


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
        """
        It seems the update function reloads the objects every time.
        No memory of objects ans places, but total perception
        """
        where = []
        what = []
        color_map = dict(green=1, red=-1)
        self.n_objects = 0
        # Seems like the agent sees the whole world here?
        for obj in world.agents:
            if obj is not self.body:
                angle, dist = self.compute_angle_and_distance(obj)
                color = color_map[obj.color]
                
                if dist < 1:
                    dist = 1.0
                    
                r = 1.0/dist
                print "r:", r
                print "dist:", dist
                where.extend([np.sin(angle)*r, np.cos(angle)*r, r])
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
    # Does the 
    turn = nengo.Ensemble(n_neurons=50, dimensions=1)
    speed = nengo.Ensemble(n_neurons=50, dimensions=1)
    cn = nengo.Connection(speed, body_speed)
    print(cn.pre)
    nengo.Connection(turn, body_turn)
    
    # create sensors and neurons to hold the sensors.  We are using an 
    #  EnsembleArray so that there are separate neurons to store the information
    #  for each object.
    sensors = State(body)
    
    what = nengo.networks.EnsembleArray(n_ensembles=sensors.n_objects,
                                        ens_dimensions=1,
                                        n_neurons=50)
    where = nengo.networks.EnsembleArray(n_ensembles=sensors.n_objects,
                                         ens_dimensions=3,
                                         n_neurons=100,
                                         intercepts=nengo.dists.Uniform(0.1, 1.0))
    nengo.Connection(sensors[:sensors.n_objects], what.input, synapse=None)
    nengo.Connection(sensors[sensors.n_objects:], where.input, synapse=None)
    # So this splits the sensor inputs to the What and Where stream?
    # Right, because the what and where lists are concatenated in the update function. 
    
    
    # Now let's implement the simplest possible behaviour: turn towards objects.
    def turn_towards(x):
        print("Turn x", x)
        if x[0] < -0.1:
            return 1
        elif x[0] > 0.1:
            return -1
        else:
            return 0
            
    # Stop moving if object is close
    def toggle_speed(x):
        # If r is big, ball is close
        if x[2] > 0.9: 
            return 0
        else: 
            return -0.3
        
        
        
    # do the above function for all the objects
    for i in range(sensors.n_objects):
        nengo.Connection(where.ensembles[i], turn, function=turn_towards)
    
    # Decrease speed if seeing a Threat
    # nengo.Connection(what.ensembles[1], speed, function=toggle_speed)
    nengo.Connection(where.ensembles[0], speed, function=toggle_speed)
    
    
    # and let's just move forward at a fixed speed.
    fixed_speed = nengo.Node(0.3)
    nengo.Connection(fixed_speed, speed)

    # Some probes
with model:
    probe_turn = nengo.Probe(turn, sample_every=0.1)
    probe_speed = nengo.Probe(speed, sample_every=0.1)
    probe_where = nengo.Probe(where.output, sample_every=0.1)
    probe_sensors = nengo.Probe(sensors, sample_every=0.1)


sim = nengo.Simulator(model)    # Create the simulator
sim.run(1)                    # Run it for 1 seconds
print "sensors_output" 
print sim.data[probe_sensors]

p = sim.data[probe_sensors]
sinr = p[0][2]
cosr = p[0][3]
print sinr, cosr
ar = np.arctan(sinr/cosr)
print ar

#print sim.data[probe_where:10]


#print "Target: ", probe_turn.target
#print "Attr: ", probe_turn.attr
#print "Sim.data turn: ", sim.data[probe_turn][:10]
#print "Sim.data speed: ", sim.data[probe_speed][:10]
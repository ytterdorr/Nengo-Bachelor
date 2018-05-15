import nengo
import nengo.spa as spa
import numpy as np
import math

class State(nengo.Node):
    
    def __init__(self):
        self.var = 1
        super(State, self).__init__(self.update)
    
    def food_input(self, t):
        if self.var > 0.9:
            return "NOFOOD" #vocab.parse("NOFOOD")
        else:
            return "FOOD"
            #return "FOOD" #vocab.parse("FOOD")
        
    def update(self, t):
        if t > 0.2:
            self.var = 0

def action_output(t, action):

    result = np.dot(action, vocab.parse("WAIT").v)

    return result

def action_input(t):
    counter = math.floor(t*10)
    if counter % 4 < 2:
        return "CHECK_FOOD"
    else:
        return "WAIT"


dimensions = 32

vocab = spa.Vocabulary(dimensions)
model = spa.SPA(label='food_input')

with model:
    
    sense = State()
    model.food = spa.State(dimensions, vocab)
    model.food_percept = spa.State(dimensions, vocab, feedback=1, feedback_synapse=0.1)
    model.current_action = spa.State(dimensions, vocab, feedback=1, feedback_synapse=0.01)

    actions = spa.Actions(
        'dot(current_action, CHECK_FOOD) --> food_percept=food',
        'dot(food, FOOD) --> food=STOP, current_action=STOP'
        )

    model.bg = spa.BasalGanglia(actions=actions)
    model.thal = spa.Thalamus(model.bg)

    #input_food = nengo.Node(food_input)
    model.food_input = spa.Input(food=sense.food_input, current_action=action_input)

    # Output
    action_node = nengo.Node(action_output, size_in=dimensions)
    nengo.Connection(model.current_action.output, action_node)
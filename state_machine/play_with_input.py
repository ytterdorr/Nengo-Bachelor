import nengo
import nengo.spa as spa


dimensions = 32

model = spa.SPA(label='Play_w_input')

with model:
	model.subgoal = spa.State(dimensions)
	model.food = spa.State(dimensions=dimensions)
	model.food_percept = spa.State(dimensions=dimensions)
	model.now_state = spa.State(dimensions=dimensions, feedback=1, feedback_synapse=0.01)

	actions = spa.Actions(
	    'dot(now_state, START) --> now_state=CHECK_FOOD',
	    'dot(now_state, CHECK_FOOD) --> food_percept=food',
	    'dot(now_state, CHECK_FOOD) --> now_state=ACTION',
	    'dot(now_state, ACTION) --> food_percept=WAITING',
	    'dot(food, FOOD) --> subgoal=EAT',
	    'dot(food, FOOD) --> now_state=STOP',
	    'dot(subgoal, EAT) --> subgoal=ACTION',
		)


	model.bg = spa.BasalGanglia(actions=actions)
	model.thal = spa.Thalamus(model.bg)

def food_input(t):
	if t < 0.2:
		return "NOFOOD"
	else:
		return "FOOD"

def state_input(t):
    if t < 0.1:
        return "START"
    else:
        return '0'

# Input
with model:
	model.food_input = spa.Input(food=food_input)
	model.state_input = spa.Input(now_state=state_input)
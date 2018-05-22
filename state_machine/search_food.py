import nengo
import nengo.spa as spa
import numpy as np


D = 32
vocab = spa.Vocabulary(D)
model = spa.SPA(label="SearchFood")


def food_input(t):
	if t < 0.3:
		return "NOFOOD"
	else:
		return "FOOD"

def starter(t):
    if t < 0.1:
        return "START"
    else:
        return "0"

		
with model:

		

	model.subgoal = spa.State(D)
	model.action_state = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)
	model.food_percept = spa.State(D)
	model.food_state = spa.State(D, vocab=vocab, feedback=1, feedback_synapse=0.01)


	actions = spa.Actions(
		'dot(action_state, START)*0.6 -2*dot(food_percept, FOOD) --> action_state=CHECK1',
		'dot(action_state, CHECK1)*0.6 -2*dot(food_percept, FOOD) --> action_state=TURN, food_percept=food_state',
		'dot(action_state, TURN)*0.6 -2*dot(food_percept, FOOD) --> action_state=CHECK2*0.2',
		'dot(action_state, CHECK2)*0.6 -2*dot(food_percept, FOOD) --> action_state=FORWARD, food_percept=food_state',
		'dot(action_state, FORWARD)*0.6 -2*dot(food_percept, FOOD) --> action_state=CHECK1*0.2',
		'dot(food_percept, FOOD)*0.6 --> action_state=STOP, subgoal=SEEK_FOOD',
		)

	model.bg = spa.BasalGanglia(actions=actions)
	model.thal = spa.Thalamus(model.bg)

	## Inputs and outputs
	model.food_input = spa.Input(food_state=food_input)
	model.start_input = spa.Input(action_state=starter)

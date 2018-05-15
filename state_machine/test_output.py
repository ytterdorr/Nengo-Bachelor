# Test binding output

import nengo
import nengo.spa as spa
import numpy as np


dimensions = 32

vocab = spa.Vocabulary(dimensions)
model = spa.SPA(label='Play_w_input')

def my_output(t, x):
	# How similar is x to STOP?
	eat = np.dot(x, vocab.parse('STOP').v)

	return eat

def my_input():
    pass


with model:
	model.subgoal = spa.State(dimensions, vocab)
	model.food = spa.State(dimensions, vocab)
	model.food_percept = spa.State(dimensions, vocab, feedback=1, feedback_synapse=0.1)
	model.now_state = spa.State(dimensions, vocab, feedback=1, feedback_synapse=0.01)

	actions = spa.Actions(
	    'dot(now_state, START) --> now_state=CHECK_FOOD',
	    'dot(now_state, CHECK_FOOD) --> food_percept=food, now_state=ACTION',
	    'dot(now_state, ACTION) - 10*dot(food_percept, FOOD) --> now_state=CHECK_FOOD',
	    'dot(food_percept, FOOD) --> now_state=STOP',
		)


	model.bg = spa.BasalGanglia(actions=actions)
	model.thal = spa.Thalamus(model.bg)

	output = nengo.Node(my_output, size_in=dimensions)

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
	input_food = nengo.Node(food_input)
	model.food_input = spa.Input(food=food_input)
	model.state_input = spa.Input(now_state=input_food.output)

# Output
	nengo.Connection(model.now_state.output, output)
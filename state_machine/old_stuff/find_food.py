import nengo
import nengo.spa as spa
import numpy as np


D = 32
vocab = spa.Vocabulary(D)
food_vocab = spa.Vocabulary(D)
sub_vocab = spa.Vocabulary(D)

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

	model.find_state = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.01)
	model.go_state = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.01)
	model.perception = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.05)
	model.subgoal = spa.State(dimensions=D, vocab=vocab, feedback=1, feedback_synapse=0.01)
	model.food_exists = spa.State(dimensions=D, vocab=vocab)
	model.food_close = spa.State(dimensions=D, vocab=vocab)

	actions = spa.Actions(
		# What is the stop condition?
		'dot(perception, FOOD) --> find_state=STOP, subgoal=START_GO_TO_FOOD',
		### FIND FOOD 
		'dot(subgoal, START_FIND_FOOD) --> find_state=START, subgoal=FIND_FOOD',
		'dot(find_state, START) - dot(perception, FOOD) --> find_state=CHECK1',
		'dot(find_state, CHECK1) - dot(perception, FOOD) --> perception=food_exists, find_state=WAIT1',
		'dot(find_state, WAIT1) - dot(perception, FOOD) --> find_state=TURN',
		'dot(find_state, TURN) - dot(perception, FOOD) --> find_state=CHECK2',
		'dot(find_state, CHECK2) - dot(perception, FOOD) --> perception=food_exists, find_state=WAIT2',
		'dot(find_state, WAIT2) - dot(perception, FOOD) --> find_state=FORWARD',
		'dot(find_state, FORWARD) - dot(perception, FOOD) --> find_state=CHECK1',
		### GO TO FOOD
		'dot(subgoal, START_GO_TO_FOOD) --> go_state=START, subgoal=GO_TO_FOOD',
		'dot(go_state, START) --> go_state=CHECK1',
		'dot(go_state, CHECK1) --> go_state=WAIT1, perception=food_close',
		'dot(go_state, WAIT1) - dot(perception, CLOSE) --> go_state=TURN',
		'dot(go_state, TURN) - dot(perception, CLOSE) --> go_state=FORWARD',
		'dot(go_state, FORWARD) - dot(perception, CLOSE) --> go_state=CHECK1',
		'dot(perception, CLOSE) --> go_state=STOP',
		) 
	model.bg = spa.BasalGanglia(actions=actions)
	model.thal = spa.Thalamus(model.bg)

	# Input
	model.start_input = spa.Input(subgoal=starter)
	model.exists_input = spa.Input(food_exists=food_exist_func)
	model.food_close_input = spa.Input(food_close=food_close_func)

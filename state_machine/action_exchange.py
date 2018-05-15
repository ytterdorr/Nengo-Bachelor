import nengo
import nengo.spa as spa
import numpy as np
import time


dimensions = 32
vocab = spa.Vocabulary(dimensions)
model = spa.SPA(label='ActionExchange')

"""
class ActionState(nengo.Node):

	def __init__(self):
		self.action = "WAIT"
		super(ActionState, self).__init__(self.update)
	
	def parse_action(t, action):
		turn = vocab.parse("TURN").v
		wait = vocab.parse("WAIT").v

		if np.dot(action, turn) > np.dot(action, wait):
			self.turn()
			return "WAIT"


	def turn():
		time.sleep(2)
		pass

	def update(self, t):
		if self.action == "TURN":
			self.turn()
		pass
"""

def starter(t):
	if t < 0.1:
		return "START"
	else:
		return "0"

def return_next(t):
    if t > 0.4:
        return vocab.parse("NEXT").v
    else:
        return vocab.parse("0").v

with model:
	# Nodes
	#action_node = ActionState()
	model.action_state = spa.State(dimensions, vocab=vocab, feedback=1, feedback_synapse=0.01)

	action_rules = spa.Actions(
		'dot(action_state, START)*0.6 --> action_state=TURN',
		#'dot(action_state, DONE)*0.6 --> action_state=FORWARD',
		'dot(action_state, TURN)*0.6 --> action_state=WAIT',
		#'dot(action_state, WAIT)*0.6 --> action_state=GO',
		#'dot(action_state, GO)*0.6 --> action_state=DRIVE',
		#'dot(action_state, DRIVE)*0.6 --> action_state=TURN',
		)

	# Basal Ganglia and Thalamus
	model.bg = spa.BasalGanglia(actions=action_rules)
	model.thal = spa.Thalamus(model.bg)

def action_parse(t, actions):
	turn = vocab.parse("TURN").v
	wait = vocab.parse("WAIT").v
	go = vocab.parse("GO").v
	drive = vocab.parse("DRIVE").v
	# Check matches
	turn_match = np.dot(turn, actions)
	wait_match = np.dot(wait, actions)
	go_match = np.dot(go, actions)
	drive_match = np.dot(drive, actions)
	return [turn_match, wait_match, go_match, drive_match]
	
def check_turn(t, action):
    turn_match = np.dot(action, vocab.parse("TURN").v)
    if turn_match > 1:
    	return 1
    else:
    	return 0

def read_turn(t, value):
	if value > 0.5:
		return "WAIT"
		
def turn_function(t, turn_value):
    if turn_value > 0.95:
        time.sleep(2)
        return "NEXT"

with model:
	action_parser = nengo.Node(action_parse, size_in=dimensions)
	#turn_check = nengo.Node(check_turn, size_in=dimensions)
	#turn_complete = nengo.Node(turn_function, size_in=1)
	return_next_node = nengo.Node(return_next)
	
	# Input
	model.action_input = spa.Input(action_state=starter)
	#model.turn_input = spa.Input(action_state=return_next_node.output)
	#action_ensemble = nengo.EnsembleArray()

	# Output
	nengo.Connection(model.action_state.output, action_parser)
	nengo.Connection(return_next_node, model.action_state.input)
	#nengo.Connection(model.action_state.output, turn_check)
	#nengo.Connection(turn_check, turn_complete)


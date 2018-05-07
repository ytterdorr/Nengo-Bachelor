import nengo
import nengo.spa as spa

D = 32

model = spa.SPA()
with model:
	model.goal = spa.State(D)
	model.subgoal = spa.State(D)
	model.perception = spa.State(D)
	model.now_state  = spa.State(D, feedback=1)

	actions = spa.Actions(
		'now_state = goal * perception',
		)

	model.cortical = spa.Cortical(actions)
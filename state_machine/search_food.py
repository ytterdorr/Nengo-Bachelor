import nengo
import nengo.spa as spa

model = spa.SPA()
with model:
    """
    food_input = nengo.Node(0)
    food = nengo.Ensemble(n_neurons=50, dimensions=1)
    step1 = nengo.Ensemble(n_neurons=50, dimensions=1)
    step2 = nengo.Ensemble(n_neurons=50, dimensions=1)


    # 

    #Is there food?
    def food_check(food):
        if food >0.5:
            return 1
        else:
            return 0

    #nengo.Connection(food_input, food, function=food_check)
    """
    
    
    D = 32
    #step = nengo.Node(0)
    model.food = spa.State(D)
    model.now_state = spa.State(D, feedback=1, feedback_synapse=0.01)
    model.now_action = spa.State(D, feedback=1, feedback_synapse=0.01)
    model.subgoal = spa.State(D)
    def update_step():
        pass
        
    actions = spa.Actions(
        # Start when subgoal is right
        'dot(subgoal, SEARCH_BALL) -->now_state=START',
        'dot(now_state, START) --> now_state=SEARCH1',
        'dot(now_state, START) --> subgoal=WAIT',
        'dot(now_state, SEARCH1) --> now_action=TURN',
        'dot(now_action, TURN) --> now_state=WAIT',
        'dot(now_action, TURN) --> now_action=DONE1',
        'dot(now_action, DONE1) --> now_state=SEARCH2',
        'dot(now_state, SEARCH2) --> now_action=FORWARD',
        'dot(now_action, FORWARD) --> now_state=WAIT',
        'dot(now_action, FORWARD) --> now_action=DONE2',
        'dot(now_action, DONE2) --> now_state=SEARCH1',
        'dot(food, ISFOOD) --> now_state=STOP',
        )
    
    model.bg = spa.BasalGanglia(actions)
    model.thalamus = spa.Thalamus(model.bg)

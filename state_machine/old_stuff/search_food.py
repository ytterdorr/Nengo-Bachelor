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
    
    
    D = 64
    #step = nengo.Node(0)
    model.food = spa.State(D)
    model.now_state = spa.State(D)
    model.now_action = spa.State(D)
    model.subgoal = spa.State(D)
    def update_step():
        pass
        
    actions = spa.Actions(
        # Start when subgoal is SEARCH_BALL
        'dot(subgoal, SEARCH_BALL) -->now_state=START',
        'dot(now_state, START) --> subgoal=WAIT, now_state=SEARCH1',
        #Search, then turn
        'dot(now_state, SEARCH1) --> now_action=TURN',
        'dot(now_action, TURN) --> now_state=WAIT, now_action=DONE1',
        # Then search again and then move forward
        'dot(now_action, DONE1) --> now_state=SEARCH2',
        'dot(now_state, SEARCH2) --> now_action=FORWARD',
        'dot(now_action, FORWARD) --> now_state=WAIT, now_action=DONE2',
        # Then repeat
        'dot(now_action, DONE2) --> now_state=SEARCH1',
        # Stop when food is found
        'dot(food, ISFOOD) --> now_state=STOP',
        )
    
    def subgoal_input(t):
        if t < 0.1:
            return 'SEARCH_BALL'
        else:
            return '0'
    
    model.bg = spa.BasalGanglia(actions)
    model.thalamus = spa.Thalamus(model.bg)
    model.sub_input = spa.Input(subgoal=subgoal_input)

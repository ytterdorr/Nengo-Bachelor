#search_food_swiches.py

success = True

switch(goalStep) {
	
	case(0): #START 
		if(food_ball_count > 0):
			goalStep=3 # SEEK
		else:
			goalStep=1 # RANDOM_TURN
	
	case(1): # RANDOM_TURN
		random_turn()
		goalStep=2
	
	case(2): # MOVE_FORWARD
		move_forward_one_second()

	case(3): # SEEK
		if (get_closer_to_ball() == success):
			goalStep = 4 # STOP
		else: 
			scan()

	case(4): # at ball
		robot.Stop()
		goalStep = 5 # Recharge Health

	case(5) #Health

}

### Action A : Searching for Food

"""
Same as for Finding Safe Area. 
"""

### Action B : Finding Safe Area

steps = {
	0: "START"
	1: "CHECK1 FOR SAFE BALL"
		if safe_area detected:
			go to Seek Safe Ball.
		else: 
			go to step 2 (turn)
}	2: "TURN"
		THEN go to step 3 (check2)
	3: "CHECK2"
		if safe_area detected:
			go to Seek Safe Ball
		else:
			go to step 4 (forward)
	4: "FORWARD"
		THEN go to step 1 (check1)




### Action C : Seeking an Objective Ball

steps = {
	0: "START",
	1: "CHECK_IR_SENSOR",
	2: "FIND_CLOSEST_BALL",
	3: "COMPUTE ANGLE",
		if angle is close:
			go to step 4 (compute distance)
		else:
			go to step 6 (which side)
	4: "COMPUTE DISTANCE"
	5: "MOVE 3/4 of distance"
		THEN go to step 1
	
	# This has branched.
	6: "WHICH SIDE?"
		if side is left:
			turn=left
		else:
			turn=right
	7: "TURN 3/4 of angle"
		THEN go to step 1

}

### Action D : Scanning for 'lost' Objective Ball

steps = {
	0: "CHECK FOR BALL"
		if ball detected:
			END (Go back to previous goal)
		else:
			go to step 1
	1: "TURN 45 degrees right"
		THEN go to step 2
	2: "TURN 15 degreees"
		Repeat 6 times or so
	3: "TURN 45 degrees back to starting position" 
}	

### Action E : Avoid Danger Balls

steps = {
	1: "COMPUTE CLOSEST BALL"
		if on_left:
			turn = "left"
		else:
			turn = "right"
		go to TURN
	2: "EXECUTE TURN"
		Generate a number >30
		set direction to turn #left/right)
		turn
	3: "MOVE FORWARD"
}



### Action F : Avoid ball

steps = {
	1: "STOP ROBOT"
	2: "CHECK DISTANCE SENSOR"
		if not close:
			go to END
		else:
			go to step 3 (TURN)
	3: "TURN"
		direction = random("LEFT", "RIGHT")
			turn by 45 degrees in direction
		THEN go to step 2 ("CHECK DISTANCE SENSOR")
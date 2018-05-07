import nengo

# Avoid boundary walls
"""
Start

if IR reading < 15:
	1. Randomly choose left or right
	2. Turn by 45 degrees
else: 
	End

Can I use random in Nengo? 
"""

model = nengo.Network()
with model: 

	IR_sensor = nengo.Node(0)

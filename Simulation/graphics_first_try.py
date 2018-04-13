from graphics import *
from random import randint
from time import sleep

print("Yay")

"""
TODOs

Events
- Danger Encountered
- Found Food
- Returned to Safe Area
- Wall Encountered
- Health Too Low

Movement
Find Closest Food

Perception

Wall collisions

Actions


"""

# window parameters
w = {
	"width": 400,
	"height": 400,
	"background": "green4"
}

# Safe zone parapmeters
sf = {
	"width": 120,
	"color": 'yellow'
}

# balls parameters
b = {
	"radius": 10,
	"foodColor": "green1",
	"threatColor": "red3",
	
}

# Robot parameters
r = {
	"hunger": 100,
	"color": "blue",
	"x": 15,
	"y": 15,
	"width":30
}

win = GraphWin("This is a window", w["width"], w["height"], autoflush=False)
win.setBackground(w["background"])


# Foods and threats numbers
num_foods = 2
num_threats = 0

# Draw Safe Zone
safe_zone = Polygon(Point(0,0), Point(0, sf['width']), Point(sf['width'], 0))
safe_zone.setFill(sf['color'])
safe_zone.draw(win)

# Setup foods

foods = []
for i in range(num_foods):
	# Get a random point

	fx = randint(sf["width"], w["width"]-b["radius"])
	fy = randint(sf["width"], w["height"]-b["radius"])
	#TODO Check so circles don't overlap
	cir = Circle(Point(fx, fy), b["radius"])
	cir.setFill(b['foodColor'])
	foods.append(cir)
	foods[i].draw(win)

threats = []
for i in range(num_threats):
	# Get a random point
	fx = randint(sf["width"], w["width"]-b["radius"])
	fy = randint(sf["width"], w["height"]-b["radius"])
	#TODO Check so circles don't overlap
	cir = Circle(Point(fx, fy), b["radius"])
	cir.setFill(b["threatColor"])
	threats.append(cir)
	threats[i].draw(win)

# Setup Robot
robot = Rectangle(Point(r["x"], r["y"]), Point(r["x"]+r["width"], r["y"]+r["width"])) 
robot.setFill(r["color"])
robot.draw(win)

# Info displays
hunger_display = Text(Point(w['width']/2, w["height"]-30), "HUNGER: "+str(r["hunger"]))
hunger_display.draw(win)

def find_closest_food():
	pass





def update_hunger():
	r["hunger"] -= 1
	hunger_display.setText("HUNGER: " + str(r["hunger"]))

def update_stuff():
	update_hunger()
	update()

def main():
	sleep(2)
	update_stuff()

update()
while(1):
	main()
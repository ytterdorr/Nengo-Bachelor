// Depends on Snap being imported at beginning of HTML document

s = Snap("#svg-canvas");


// Emotions
var anger = {w0: 0, w1: 1.9, w2: 0.15, gamma: 0.92},
fear = {w0: 0, w1: 1.9, w2: 0.15, gamma: 0.92},
happiness = {w0: 0, w1: 2.3, w2: 0.15, gamma: 0.92},
surprise = {w0: 0, w1: 1.7, w2: 0.15, gamma: 0.88};

// Draw safe area
var safe_area = s.polygon(0,0,0,100,100,0).attr({fill: "yellow", stroke:"black"});

// Create robot
var robot = s.rect(15, 15, 30, 30);
robot.attr({
	fill: "blue",
	"hunger": 100,
	"anger": 100,
	"fear": 100, 
	"happiness": 100,
	"speed": 90
});


// Circle attributes
var b_rad = 13;
var food_color = "green";
var threat_color = "red";

// Draw Food and Threat circles
var food1 = s.circle(100, 100, b_rad);
food1.attr({
	fill: food_color
});

var threat1 = s.circle(200, 100, b_rad);
threat1.attr({
	fill: threat_color
});

// Setup DATA display
sd = Snap("#svg-data-display");

// What data to display?
/*

*/
var hunger_data = sd.text(10, 20, "Hunger: "+robot.attr("hunger"));
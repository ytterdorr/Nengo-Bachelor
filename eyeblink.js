var s = Snap("#svg-canvas")

var circle_1 = s.circle(300, 200, 140);
var circle_2 = s.circle(250, 200, 140);
 
// Group circles together
 
var circles = s.group(circle_1, circle_2);
 
var ellipse = s.ellipse(275, 220, 170, 90);
 
// Add fill color and opacity to circle and apply
// the mask
circles.attr({
  fill: 'coral',
  fillOpacity: 0.6,
  mask: ellipse
});
 
ellipse.attr({
  fill: '#fff',
  opacity: 0.8
});
 
// Create a blink effect by modifying the rx value
// for ellipse from 90px to 1px and backwards
 
function blink(){
  ellipse.animate({ry:1, rx: 120}, 220, function(){
    ellipse.animate({ry: 90, rx: 10}, 300);
  });
}
 
// Recall blink method once every 3 seconds
 
setInterval(blink, 3000);
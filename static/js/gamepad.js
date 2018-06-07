/*
 * Gamepad API Test
 * Written in 2013 by Ted Mielczarek <ted@mielczarek.org>
 *
 * To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
 *
 * You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
 */
var haveEvents = 'GamepadEvent' in window;
var haveWebkitEvents = 'WebKitGamepadEvent' in window;
var controllers = {};
var rAF = window.requestAnimationFrame ||
  window.mozRequestAnimationFrame ||
  window.webkitRequestAnimationFrame;

setInterval(updateStatus, 200);
function connecthandler(e) {
    addgamepad(e.gamepad);
	console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
    e.gamepad.index, e.gamepad.id,
    e.gamepad.buttons.length, e.gamepad.axes.length);
}
function addgamepad(gamepad) {
  controllers[gamepad.index] = gamepad; 
}

function disconnecthandler(e) {
    removegamepad(e.gamepad);
	console.log("Gamepad disconnected from index %d: %s",
    e.gamepad.index, e.gamepad.id);
}

function removegamepad(gamepad) {
  var d = document.getElementById("controller" + gamepad.index);
  document.body.removeChild(d);
  delete controllers[gamepad.index];
}

function updateStatus() {
  scangamepads();
  var bots = new Array();
  for (j in controllers) {
    var controller = controllers[j];
	var flag = false;
    for (var i=0; i<controller.buttons.length; i++) {
      var val = controller.buttons[i];
      var pressed = val == 1.0;
      if (typeof(val) == "object") {
        pressed = val.pressed;
        val = val.value;
      }
	  bots[i] = pressed;
	  if (pressed) flag = true;
    } 
	for (var i=0;i<controller.axes.length; i++) 
		if (Math.abs(controller.axes[i])>0.05) flag = true;
	if (flag)
	  $.ajax({
		url: "/gamepad_data",
		type: "POST",
		data: JSON.stringify({axes: controller.axes, bottons: bots}),
		contentType: "application/json; charset=utf-8",
		success: function(dat) { 
            var div = document.getElementById("Message Box");
			if (dat!="")
            div.textContent = dat;
            console.log(dat); 
        }
	});
	break;
  }
}

function scangamepads() {
  var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
  for (var i = 0; i < gamepads.length; i++) {
    if (gamepads[i]) {
      if (!(gamepads[i].index in controllers)) {
          controllers[gamepads[i].index] = gamepads[i];
      } else {
        controllers[gamepads[i].index] = gamepads[i];
      }
    }
  }
}
function removegamepad(gamepad) {
  delete controllers[gamepad.index];
}
if (haveEvents) {
  window.addEventListener("gamepadconnected", connecthandler);
  window.addEventListener("gamepaddisconnected", disconnecthandler);
} else if (haveWebkitEvents) {
  window.addEventListener("webkitgamepadconnected", connecthandler);
  window.addEventListener("webkitgamepaddisconnected", disconnecthandler);
}
function shoot(){
	$.ajax({
		url: "/shoot",
		type: "GET", 
		success: function(msg){console.log(msg);}
		});	
}
function start(){
	$.ajax({
		url: "/start",
		type: "GET", 
		success: function(msg){console.log(msg);}
		});	
}
function end(){
	$.ajax({
		url: "/end",
		type: "GET", 
		success: function(msg){console.log(msg);}
		});	
}

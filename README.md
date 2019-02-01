# rosbridge_stick
Control a ROS-based robot using rosbridge through a gamepad/joystick.

#### Tested with: 
- [x] Logitech F710 Gamepad
- [x] Thrustmaster T.Flight Stick X

## HTML steps
Set the master URL:
```
var ros = new ROSLIB.Ros({
  url : 'ws://192.168.12.20:9090'
});
```

Open the `.html` file with a browser (tested with Chrome).

Press any button if the output shows that joystick/gamepad is not being detected.

## Python steps

`roslibpy` and `inputs` libraries needed.
```
sudo pip install roslibpy inputs 
```

Run the `.py` file.

Press any button if the output shows that joystick/gamepad is not being detected.

## Logitech Gamepad use

Velocity commands are sent when `A` button is pressed and `left joystick` is used simultaneously.

## Thrustmaster Joystick use

> **NOTE:** `PRESET` button light must be red.

Velocity commands are sent when `1` button is pressed and main `joystick` is used simultaneously.

Maximum velocity is increased/decreased through the `THROTTLE` button.


###### Based on:
> The Standard ROS JavaScript Library - http://wiki.ros.org/roslibjs
>
> roslibpy: ROS Bridge library - https://roslibpy.readthedocs.io/en/latest/

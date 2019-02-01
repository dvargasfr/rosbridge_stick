#!/usr/bin/python

from __future__ import print_function
import roslibpy
import inputs

print(inputs.devices.gamepads)

BTN_TRIGGER = 0
ABS_X = 0
ABS_Y = 0
ABS_THROTTLE = 1

# Offset for XY axis values boundaries (-1 to 1)
OFFSET_XY = -128.0
# Coeficient to set X and Y axis values between -1 and 1
#COEF_XY = -128.0
# Coeficient to set X and Y axis values between -1.5 and 1.5
COEF_XY = -85.333

# Offset for THROTTLE axis values boundaries (ex.: 0.5 => 0.5 - 1.5)
OFFSET_THROTTLE = 0.0
# Coeficient to set THROTTLE axis values between 0 and 1
COEF_THROTTLE = 255.0



#ros = roslibpy.Ros(host='192.168.12.20', port=9090)
ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
talker = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')
try:
    while True:
        events = inputs.get_gamepad()
        for event in events:
            if event.code == 'BTN_TRIGGER':
                BTN_TRIGGER = event.state;
            if event.code == 'ABS_X':
                ABS_X = (event.state + OFFSET_XY) / COEF_XY;
            if event.code == 'ABS_Y':
                ABS_Y = (event.state + OFFSET_XY) / COEF_XY;
            if event.code == 'ABS_THROTTLE':
                ABS_THROTTLE = ((COEF_THROTTLE - event.state) / COEF_THROTTLE) + OFFSET_THROTTLE;
                #ABS_THROTTLE = event.state;
            if BTN_TRIGGER == 1:
                print('Trigger ', BTN_TRIGGER)
                print('X ', ABS_X)
                print('Y ', ABS_Y)
                print('Throttle ',ABS_THROTTLE)
                talker.publish(roslibpy.Message({
                    'linear': {
                        'x':ABS_Y*ABS_THROTTLE,
                        'y':0.0,
                        'z':0.0},
                    'angular':{
                        'x':ABS_THROTTLE,
                        'y':0.0,
                        'z':ABS_X*ABS_THROTTLE
                    }}))
except KeyboardInterrupt:
    pass

ros.terminate()

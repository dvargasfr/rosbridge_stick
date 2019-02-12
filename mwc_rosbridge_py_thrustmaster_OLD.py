#!/usr/bin/python

from __future__ import print_function
from threading import Thread
import roslibpy
import inputs
from inputs import devices
from inputs import get_gamepad
import time

print(inputs.devices.gamepads)
for device in devices:
        print(device)
BTN_TRIGGER = 0
ABS_X = 0
ABS_Y = 0
ABS_THROTTLE = 1
GO_FORWARD = 1

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

freq_cnt = 0

#ros = roslibpy.Ros(host='192.168.12.20', port=9090)
ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
talker = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')

def get_gamepad_events():
    global BTN_TRIGGER
    global ABS_X
    global ABS_Y
    global OFFSET_XY
    global COEF_XY
    global GO_FORWARD
    global ABS_THROTTLE
    global COEF_THROTTLE
    global OFFSET_THROTTLE
    while True:
        events = inputs.get_gamepad()
        for event in events:
            if event.code == 'BTN_TRIGGER':
                BTN_TRIGGER = event.state;
            if event.code == 'ABS_X':
                ABS_X = (event.state + OFFSET_XY) / COEF_XY * GO_FORWARD;
            if event.code == 'ABS_Y':
                ABS_Y = (event.state + OFFSET_XY) / COEF_XY;
                if(ABS_Y < -0.05):
                    GO_FORWARD = -1;
                else:
                    GO_FORWARD = 1;
            if event.code == 'ABS_THROTTLE':
                ABS_THROTTLE = (( COEF_THROTTLE - event.state) / COEF_THROTTLE) + OFFSET_THROTTLE;


try:
    thread = Thread(target = get_gamepad_events, args = ())
    thread.start()
    while True:
        time.sleep(0.1)
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
                    'x':0.0,
                    'y':0.0,
                    'z':ABS_X*ABS_THROTTLE
                }}))
        else:
            print('Trigger ', BTN_TRIGGER)
            print('X 0.0')
            print('Y 0.0')
            print('Throttle ',ABS_THROTTLE)
            talker.publish(roslibpy.Message({
                'linear': {
                    'x':0.0,
                    'y':0.0,
                    'z':0.0},
                'angular':{
                    'x':0.0,
                    'y':0.0,
                    'z':0.0
                }}))
except KeyboardInterrupt:
    thread.stop()
    cleanup_stop_thread()

ros.terminate()

#!/usr/bin/python

from __future__ import print_function
import roslibpy
import inputs

print(inputs.devices.gamepads)

BTN_TRIGGER = 0
ABS_X = 0
ABS_Y = 0
ABS_THROTTLE = 0

#ros = roslibpy.Ros(host='192.168.12.20', port=9090)
ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
try:
    while True:
        events = inputs.get_gamepad()
        for event in events:
            if event.code == 'BTN_TRIGGER':
                BTN_TRIGGER = event.state;
            if event.code == 'ABS_X':
                ABS_X = event.state;
            if event.code == 'ABS_Y':
                ABS_Y = event.state;
            if event.code == 'ABS_THROTTLE':
                ABS_THROTTLE = event.state;
            if BTN_TRIGGER == 1:
                print('Trigger ',BTN_TRIGGER)
                print('X ',ABS_X)
                print('Y',ABS_Y)
                print('Throttle ',ABS_THROTTLE)
except KeyboardInterrupt:
    pass

ros.terminate()

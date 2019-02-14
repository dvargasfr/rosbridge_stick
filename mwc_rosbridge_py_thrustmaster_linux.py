#!/usr/bin/python

from __future__ import print_function
from threading import Thread
import roslibpy
import inputs
from inputs import devices
from inputs import get_gamepad
import time
import requests
import json


#  Axis XY         -1.5  to    1.5
#  Axis Throttle   0.0   to    1.0
#  Button 1        send command
#  Button 2        down and open hook
#  Button 4        up and close hook
#  Button 5        launch mission
#  Button 9        -
#  Button 10       -
#  None            send 0s


print(inputs.devices.gamepads)
#for device in devices:
#    print(device)

BTN_TRIGGER = 0     # Button 1
BTN_THUMB = 0       # Button 2
BTN_TOP = 0         # Button 4
BTN_TOP2 = 0        # Button 5
BTN_BASE3 = 0       # Button 9
BTN_BASE4 = 0       # Button 10
ABS_X = 0           # Joystick X axis
ABS_Y = 0           # Joystick Y axis
ABS_THROTTLE = 1    # Throttle axis
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

ros = roslibpy.Ros(host='192.168.12.20', port=9090)
#ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
talker = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')
hookService = roslibpy.Service(ros, '/hook/controller/command', 'mir_hook_controller/Command')

#service = roslibpy.Service(ros, '/rosapi/topics', 'rosapi/Topics')

def success_callback(result):
    print('Service response: ', result)

def error_callback(*args):
    print('Something went wrong')

def get_gamepad_events():
    global BTN_TRIGGER, BTN_THUMB, BTN_TOP, BTN_TOP2, BTN_BASE3, BTN_BASE4
    global ABS_X, ABS_Y, OFFSET_XY, COEF_XY
    global ABS_THROTTLE, COEF_THROTTLE, OFFSET_THROTTLE
    global GO_FORWARD
    while True:
        events = inputs.get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
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
            if event.code == 'BTN_THUMB':
                if event.state == 1:
                    BTN_THUMB = 1
                else:
                    BTN_THUMB = 0
            if event.code == 'BTN_TOP':
                if event.state == 1:
                    BTN_TOP = 1
                else:
                    BTN_TOP = 0
            if event.code == 'BTN_BASE3':
                if event.state == 1:
                    BTN_BASE3 = 1
                else:
                    BTN_BASE3 = 0
            if event.code == 'BTN_BASE4':
                if event.state == 1:
                    BTN_BASE4 = 1
                else:
                    BTN_BASE4 = 0
            if event.code == 'BTN_TOP2':
                if event.state == 1:
                    BTN_TOP2 = 1
                else:
                    BTN_TOP2 = 0

try:
    thread = Thread(target = get_gamepad_events, args = ())
    thread.daemon = True
    thread.start()
    while True:
        time.sleep(0.1)
        if BTN_TRIGGER == 1:
            print('Trigger ', BTN_TRIGGER)
            print('X ', ABS_X*ABS_THROTTLE)
            print('Y ', ABS_Y*ABS_THROTTLE)
            print('Throttle ', ABS_THROTTLE)
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
            #print('Trigger ', BTN_TRIGGER)
            #print('X 0.0')
            #print('Y 0.0')
            #print('Throttle ',ABS_THROTTLE)
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
        if BTN_THUMB == 1:
            print("Btn 2: baja brazo y abre gancho")
            request_close = roslibpy.ServiceRequest({'cmd':"open",'value':0})
            hookService.call(request_close, success_callback, error_callback)
            time.sleep(0.5)
            request_down = roslibpy.ServiceRequest({'cmd':"height",'value':190})
            hookService.call(request_down, None, None)
            #request = roslibpy.ServiceRequest()
            #service.call(request, success_callback, error_callback)
        if BTN_TOP == 1:
            print("Btn 4: sube brazo y cierra gancho")
            request_open = roslibpy.ServiceRequest({'cmd':"close",'value':0})
            hookService.call(request_open, None, None)
            request_up = roslibpy.ServiceRequest({'cmd':"height",'value':220})
            hookService.call(request_up, None, None)
        if BTN_BASE3 == 1:
            #print("Btn 9: sube gancho")
            #request = roslibpy.ServiceRequest({'cmd':"height",'value':220})
            #hookService.call(request, None, None)
            pass
        if BTN_BASE4 == 1:
            #print("Btn 10: baja gancho")
            #request = roslibpy.ServiceRequest({'cmd':"height",'value':190})
            #hookService.call(request, None, None)
            pass
        if BTN_TOP2 == 1:
            print("Lanzada mision!")
            url = 'http://192.168.12.20/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            payload = {'mission_id':'7f2738ff-2aaf-11e9-bbc9-94c69116b9d7'}
            r = requests.post(url, headers=headers, json=payload)
except KeyboardInterrupt:
    pass

ros.terminate()

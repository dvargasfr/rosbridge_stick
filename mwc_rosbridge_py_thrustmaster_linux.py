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

print(inputs.devices.gamepads)
#for device in devices:
#    print(device)

BTN_TRIGGER = 0     # Button 1          -   send command
BTN_THUMB = 0       # Button 2          -   down and open hook
BTN_TOP = 0         # Button 4          -   up and close hook
BTN_BASE2 = 0       # Button 8          -   launch mission
BTN_BASE3 = 0       # Button 9          -   pick up cart mission
BTN_BASE4 = 0       # Button 10         -   release cart mission
ABS_X = 0           # Joystick X axis   -   X velocity (-1.5 to 1.5)
ABS_Y = 0           # Joystick Y axis   -   Y velocity (-1.5 to 1.5)
ABS_THROTTLE = 1    # Throttle axis     -   Velocity factor (0.0 to 1.0)
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

ROBOT_IP='10.0.0.192'

ros = roslibpy.Ros(host=ROBOT_IP, port=9090)
#ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
talker = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')
hookService = roslibpy.Service(ros, '/hook/controller/command', 'mir_hook_controller/Command')
hookBrakeService = roslibpy.Service(ros, '/hook/brake/command', 'mir_hook_controller/Command')
hookStatusService = roslibpy.Service(ros, '/hook/getStatus', 'mir_srvs/getStatus')

def success_callback(result):
    print('Service response: ', result)

def error_callback(*args):
    print('Something went wrong')

def get_gamepad_events():
    global BTN_TRIGGER, BTN_THUMB, BTN_TOP, BTN_BASE2, BTN_BASE3, BTN_BASE4
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
                ABS_X = (event.state + OFFSET_XY) / COEF_XY;# * GO_FORWARD;
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
            if event.code == 'BTN_BASE2':
                if event.state == 1:
                    BTN_BASE2 = 1
                else:
                    BTN_BASE2 = 0
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

try:
    thread = Thread(target = get_gamepad_events, args = ())
    thread.daemon = True
    thread.start()
    # Start with brake on
    request_hook_brake = roslibpy.ServiceRequest({'cmd':"ON",'value':0})
    hookBrakeService.call(request_hook_brake, None, None)

    while True:
        time.sleep(0.1)
        if BTN_TRIGGER == 1:
            # Stop mission mode
            url = 'http://'+ROBOT_IP+'/?mode=set-robot-state&state=4'
            headers = {'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8', 'Cookie': 'mir_login_type=regular; mir_user_id=2; mir_user_shortcode=7280306096; PHPSESSID=jd07v8gf2lf2cujbasp1rtpsr0; menu_desktop_visible=true; mir_lang=en_US'}
            r = requests.get(url=url, headers=headers)
            # Delete every mission on queue before sending move commands
            url = 'http://'+ROBOT_IP+'/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            r = requests.delete(url=url, headers=headers)
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

        # Button 2: Launch mission pick up cart automatically
        if BTN_THUMB == 1:
            url = 'http://'+ROBOT_IP+'/?mode=set-robot-state&state=3'
            headers = {'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8', 'Cookie': 'mir_login_type=regular; mir_user_id=2; mir_user_shortcode=7280306096; PHPSESSID=jd07v8gf2lf2cujbasp1rtpsr0; menu_desktop_visible=true; mir_lang=en_US'}
            r = requests.get(url=url, headers=headers)
            print("Lanzada mision agarrar carro!")
            url = 'http://'+ROBOT_IP+'/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            payload = {'mission_id':'7d96a01e-3683-11e9-a41d-94c69116b9d7'} # pick up cart
            r = requests.post(url, headers=headers, json=payload)
        # Button 4: Launch mission leave cart automatically
        if BTN_TOP == 1:
            url = 'http://'+ROBOT_IP+'/?mode=set-robot-state&state=3'
            headers = {'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8', 'Cookie': 'mir_login_type=regular; mir_user_id=2; mir_user_shortcode=7280306096; PHPSESSID=jd07v8gf2lf2cujbasp1rtpsr0; menu_desktop_visible=true; mir_lang=en_US'}
            r = requests.get(url=url, headers=headers)
            print("Lanzada mision soltar carro!")
            url = 'http://'+ROBOT_IP+'/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            payload = {'mission_id':'d13c9796-3683-11e9-a41d-94c69116b9d7'} # leave cart
            r = requests.post(url, headers=headers, json=payload)
            time.sleep(25)
            request_down = roslibpy.ServiceRequest({'cmd':"height",'value':190})
            hookService.call(request_down, None, None)
            '''
            time.sleep(8)
            url = 'http://'+ROBOT_IP+'/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            r = requests.delete(url=url, headers=headers)
            '''
        # Button 8: Launch mission go for charging automatically
        if BTN_BASE2 == 1:
            url = 'http://'+ROBOT_IP+'/?mode=set-robot-state&state=3'
            headers = {'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8', 'Cookie': 'mir_login_type=regular; mir_user_id=2; mir_user_shortcode=7280306096; PHPSESSID=jd07v8gf2lf2cujbasp1rtpsr0; menu_desktop_visible=true; mir_lang=en_US'}
            r = requests.get(url=url, headers=headers)
            print("Lanzada mision!")
            url = 'http://'+ROBOT_IP+'/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            # payload = {'mission_id':'59ef27c1-352a-11e9-b790-94c69116b9d7'} # cuerno
            payload = {'mission_id':'b8e6fce1-350c-11e9-a984-94c69116b9d7'} # carga
            r = requests.post(url, headers=headers, json=payload)
        # Button 9: Down and open hook, and brake on
        if BTN_BASE3 == 1:
            print("Btn 2: baja brazo, abre gancho y activa freno")
            request_close = roslibpy.ServiceRequest({'cmd':"open",'value':0})
            hookService.call(request_close, success_callback, error_callback)
            time.sleep(0.5)
            request_down = roslibpy.ServiceRequest({'cmd':"height",'value':190})
            hookService.call(request_down, None, None)
            request_hook_brake = roslibpy.ServiceRequest({'cmd':"ON",'value':0})
            hookBrakeService.call(request_hook_brake, None, None)
            url = 'http://'+ROBOT_IP+'/?mode=set-robot-state&state=3'
            headers = {'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8', 'Cookie': 'mir_login_type=regular; mir_user_id=2; mir_user_shortcode=7280306096; PHPSESSID=jd07v8gf2lf2cujbasp1rtpsr0; menu_desktop_visible=true; mir_lang=en_US'}
            r = requests.get(url=url, headers=headers)
            '''
            request_status = roslibpy.ServiceRequest({})
            hookStatusService.call(request_status, success_callback, error_callback)

            url = 'http://'+ROBOT_IP+'/api/v2.0.0/mission_queue'
            headers = {'accept-language':'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6','authorization':'Basic YWRtaW46NzI3NjQ5MDg5ZTZjYmMxMDVlNGRkOTkwZGIxMDg4OTg1ZmJiOTQ0Y2Y3NWQyYzQ4ODUxMGQ1MzliMDA3NzkwZg=='}
            payload = {'mission_id':'b47879be-35ea-11e9-a094-94c69116b9d7'} # leavecart
            r = requests.post(url, headers=headers, json=payload)
            '''
        # Button 10: Up and close hook, and brake off
        if BTN_BASE4 == 1:
            print("Btn 4: sube brazo, cierra gancho y desactiva freno")
            request_open = roslibpy.ServiceRequest({'cmd':"close",'value':0})
            hookService.call(request_open, None, None)
            request_up = roslibpy.ServiceRequest({'cmd':"height",'value':230})
            hookService.call(request_up, None, None)
            request_hook_brake = roslibpy.ServiceRequest({'cmd':"OFF",'value':0})
            hookBrakeService.call(request_hook_brake, None, None)
except KeyboardInterrupt:
    # Let brake off before exit
    request_hook_brake = roslibpy.ServiceRequest({'cmd':"OFF",'value':0})
    hookBrakeService.call(request_hook_brake, None, None)
    #pass

ros.terminate()

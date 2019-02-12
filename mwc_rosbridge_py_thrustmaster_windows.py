#!/usr/bin/python

from __future__ import print_function
import roslibpy
import time
import sdl2
import sdl2.ext
sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
joystick = sdl2.SDL_JoystickOpen(0)

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
print("Connecting...")
#while(not ros.is_connected):
#    continue
print("Connected!")

talker = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')
hookService = roslibpy.Service(ros, '/hook/controller/command', 'mir_hook_controller/Command')

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
    while True:
        for event in sdl2.ext.get_events():
            if event.type==sdl2.SDL_JOYAXISMOTION:
                print ('Axis: ',[event.jaxis.axis,event.jaxis.value])
                # Eje X
                if event.jaxis.axis==0:
                    ABS_X = event.jaxis.value
                # Eje Y
                if event.jaxis.axis==1:
                    ABS_Y = event.jaxis.value
                # Eje Throttle
                if event.jaxis.axis==3:
                    ABS_THROTTLE = event.jaxis.value
            if event.type==sdl2.SDL_JOYBUTTONDOWN:
                print ('Button press: ',[event.jaxis.axis,event.jaxis.value])
                # Boton 1: send commands if pressed, else send 0s
                if event.jaxis.axis==0:
                    print ('detectado boton 1')
                    BTN_TRIGGER = 1
                # Boton 2: Close the hook
                if event.jaxis.axis==1:
                    print ('detectado boton 2')
                    request = roslibpy.SserviceRequest()
                    hookService.call(request, succes_callback, error_callback)
                # Boton 4: Open the hook
                if event.jaxis.axis==3:
                    print ('detectado boton 4')
            if event.type==sdl2.SDL_JOYBUTTONUP:
                print ('Button up: ',[event.jaxis.axis,event.jaxis.value])
                if event.jaxis.axis==0:
                    print ('detectado boton 1')
                    BTN_TRIGGER = 0


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

#!/usr/bin/python

import sdl2
import sdl2.ext
sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
joystick = sdl2.SDL_JoystickOpen(0)
#sdl2.ext.Window("test", size=(800,600),position=(0,0),flags=sdl2.SDL_WINDOW_SHOWN)
#window.refresh()
while True:
    for event in sdl2.ext.get_events():
        if event.type==sdl2.SDL_KEYDOWN:
            print (sdl2.SDL_GetKeyName(event.key.keysym.sym).lower())
        elif event.type==sdl2.SDL_JOYAXISMOTION:
            print ('Axis: ',[event.jaxis.axis,event.jaxis.value])
            if event.jaxis.axis==0:
                print ('detectado eje 0')
            if event.jaxis.axis==1:
                print ('detectado eje 1')
            # Eje Throttle
            if event.jaxis.axis==3:
                print ('detectado eje throttle')
        elif event.type==sdl2.SDL_JOYBUTTONDOWN:
            print ('Button: ',[event.jaxis.axis,event.jaxis.value])
            if event.jaxis.axis==0:
                print ('detectado boton 1')
            if event.jaxis.axis==1:
                print ('detectado boton 2')
            if event.jaxis.axis==2:
                print ('detectado boton 3')
            if event.jaxis.axis==3:
                print ('detectado boton 4')

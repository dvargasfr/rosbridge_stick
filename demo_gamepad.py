#!/usr/bin/python

import inputs

print(inputs.devices.gamepads)

while True:
    events = inputs.get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)
        #if event.code == 'BTN_TRIGGER':
        #    print(event.ev_type, event.code, event.state)
        #ABS_THROTTLE BTN_TRIGGER ABS_X ABS_Y

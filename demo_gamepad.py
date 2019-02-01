#!/usr/bin/python

import inputs

print(inputs.devices.gamepads)

while True:
    events = inputs.get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)
        #if (event.ev_code == 'BTN_SOUTH')
        #    print(event.ev_type, event.code, event.state)
        #if (event.ev_type == BTN_WEST)

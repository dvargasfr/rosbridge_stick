from __future__ import print_function
import roslibpy

print('A')
ros = roslibpy.Ros(host='192.168.12.20', port=9090)
print('B')
ros.run()
print('C')
ros.on_ready(lambda: print('Is ROS connected?', ros.is_connected))
print('D')
try:
    while True:
        pass
except KeyboardInterrupt:
    pass

ros.terminate()

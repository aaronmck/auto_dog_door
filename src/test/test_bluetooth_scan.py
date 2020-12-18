from bluepy.btle import Scanner
import pi_servo_hat
import time

# Initialize Constructor

scanner = Scanner()

scan_buffer = [-100 for i in range(10)]

for i in range(0,100):
    devices = scanner.scan(1.0)
    
    for device in devices:
        if device.addr == 'd5:dd:6b:2b:66:c1':
            print(device.rssi)
            scan_buffer = scan_buffer[1:len(scan_buffer)]
            scan_buffer.append(device.rssi)
            avg = float(sum(scan_buffer))/float(len(scan_buffer))
            if avg < -45:
                print("FAR")
            else:
                print("CLOSE")

                print("DEV = {} RSSI = {}".format(device.addr, device.rssi))

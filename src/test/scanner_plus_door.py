from bluepy.btle import Scanner
import pi_servo_hat
import smbus, time

bus = smbus.SMBus(1)
addr = 0x40

## Running this program will move the servo to 0, 45, and 90 degrees with 5 second pauses in between with a 50 Hz PWM signal.
time.sleep(1)
bus.write_byte_data(addr, 0, 0x20) # enables word writes
time.sleep(.25)
bus.write_byte_data(addr, 0, 0x10) # enable Prescale change as noted in the datasheet
time.sleep(.25) # delay for reset
bus.write_byte_data(addr, 0xfe, 0x79) #changes the Prescale register value for 50 Hz, using the equation in the datasheet.
bus.write_byte_data(addr, 0, 0x20) # enables word writes
time.sleep(.25)

# notes:
#bus.write_word_data(addr, 0x06, 0) # chl 0 start time = 0us, write a 0 position (~90+, open all the way)
#bus.write_word_data(addr, 0x08, 312) # chl 0 end time = 1.5ms (45 degrees)
#bus.write_word_data(addr, 0x08, 416) # chl 0 end time = 2.0ms (90 degrees)
#bus.write_word_data(addr, 0x08, 460) # chl 0 end time = 2.0ms (90+ degrees, fully closed)
# Initialize Constructor

current_position = 0
open_pos = 50
closed_pos = 460
jumps = 20
rssi_threshold = -50
rssi_buffer_size = 4
scan_spacing_in_secs = 1.0

class MotorDoor:
    def __init__(self,swing_range=110):
        self.open_position = 209
        self.closed_position = 460
        self.jump_dist = 20
        self.swing_range = swing_range

        self.rotation_position = 0
        self.move_to(0)
        self.is_open = True
        
    def slow_open(self):
        if not self.is_open:
            self.move_to(self.open_position)
            self.rotation_position = self.open_position
        self.is_open = True
        
    def slow_close(self):
        if self.is_open:
            self.move_to(self.closed_position)
            self.rotation_position = self.closed_position
        self.is_open = False
        
    def move_to(self,move_to_position):
        #write start and stop to channel
        bus.write_word_data(addr, 0x06, 0) # channel start time = 0us for all
        bus.write_word_data(addr, 0x08, move_to_position) # channel stop time is a special position val calculated above

door = MotorDoor()

        
scanner = Scanner()

scan_buffer = [-100 for i in range(rssi_buffer_size)]

for i in range(0,100):
    devices = scanner.scan(scan_spacing_in_secs)
    
    for device in devices:
        if device.addr == 'd5:dd:6b:2b:66:c1':
            print(device.rssi)
            scan_buffer = scan_buffer[1:len(scan_buffer)]
            scan_buffer.append(device.rssi)
            avg = float(sum(scan_buffer))/float(len(scan_buffer))
            if avg < rssi_threshold:
                print("FAR")
                door.slow_close()
            else:
                print("CLOSE")
                door.slow_open()

                print("DEV = {} RSSI = {}".format(device.addr, device.rssi))

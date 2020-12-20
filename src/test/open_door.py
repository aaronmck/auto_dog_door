from bluepy.btle import Scanner
import pi_servo_hat
import smbus, time
import datetime
import logging

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

rssi_threshold = -50
rssi_buffer_size = 2
scan_spacing_in_secs = 1
seconds_door_stays_open = 30

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""Dog door monitor v1""")


epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0
class MotorDoor:
    def __init__(self,swing_range=110):
        self.open_position = 240
        self.closed_position = 420
        self.jump_dist = 5
        self.swing_range = swing_range

        self.rotation_position = self.closed_position
        self.move_to(self.closed_position)
        self.opened_time = datetime.datetime.now().timestamp() - 100
        self.is_open = False

    def slow_open(self):
        if not self.is_open:
            logging.info("Opening door")
            for i in range(self.closed_position,self.open_position,-1 * self.jump_dist):
                self.move_to(i)
                time.sleep(0.1)
            self.rotation_position = self.open_position
            self.opened_time = datetime.datetime.now().timestamp()
        else:
            self.move_to(self.open_position) # keep forcing open
        self.is_open = True
        
    def slow_close(self):
        if self.is_open:
            tm = datetime.datetime.now().timestamp()
            if tm - self.opened_time > 30:
                logging.info("Closing door")
                for i in range(self.open_position,self.closed_position,self.jump_dist):
                    self.move_to(i)
                    time.sleep(0.1)
                self.move_to(self.closed_position)
                self.rotation_position = self.closed_position
                self.is_open = False
            else:
                logging.info("Door not closed due to timeout")
        else:
            self.move_to(self.closed_position) # keep forcing open
        
    def move_to(self,move_to_position):
        #write start and stop to channel
        bus.write_word_data(addr, 0x06, 0) # channel start time = 0us for all
        bus.write_word_data(addr, 0x08, move_to_position) # channel stop time is a special position val calculated above

door = MotorDoor()
door.slow_open()

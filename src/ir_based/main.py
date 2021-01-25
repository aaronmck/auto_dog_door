from motor_door import *
import argparse

from smbus import SMBus
import time

addr = 0x08 # bus address
bus = SMBus(1) # indicates /dev/ic2-1


parser = argparse.ArgumentParser(description='Automate the dog door')
parser.add_argument('--logfile', help='the log file to write to',required=True)

args = parser.parse_args()

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


logfile=open(args.logfile,"w")

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""Dog door monitor v1""")

from enum import Enum
class Door(Enum):
    INIT_OPEN = 1
    PASS_THROUGH_OPEN = 2
    HOLD_OPEN = 3
    INIT_CLOSE = 4
    PASS_THROUGH_CLOSE = 5
    CLOSED = 6

class DoorState:
    def __init__(self,door,bus,start_open=False,min_open_dist=250,min_open_secs=30):
        self.door = door
        self.door_state = Door.CLOSED
        if start_open == Door.HOLD_OPEN:
            self.door_state = Door.CLOSED
        self.min_open_secs = min_open_secs
        self.min_open_dist = min_open_dist # sensor distance, in mm
        self.bus = bus
        
        if start_open:
            door.slow_open()
        else:
            door.slow_close(self.min_open_secs)

    def read_distances(self):
        block = self.bus.read_i2c_block_data(addr, 0, 4)
        self.dist1 = block[0]<<8 | block[1]
        self.dist2 = block[2]<<8 | block[3]


    def decide(self):
        pre_state = self.door_state
        
        if self.door_state == Door.INIT_OPEN:
            if self.dist1 < self.min_open_dist and self.dist2 < self.min_open_dist:
                pass # we're already in the opening stage
            elif self.dist1 < self.min_open_dist:
                pass # we're already in the opening stage
            elif self.dist2 < self.min_open_dist:
                self.door_state = Door.PASS_THROUGH_OPEN # they've passed through (door1 > min)
            else: # neither
                # this one is tricky; either it's a false alarm or they've passed through too quickly; we'll say false alarm
                self.door_state = Door.CLOSED
                door.slow_close(self.min_open_secs)
                
        elif self.door_state == Door.PASS_THROUGH_OPEN:

            if self.dist1 < self.min_open_dist and self.dist2 < self.min_open_dist:
                # this is confusing; we'll go back to the open state
                self.door_state = INIT_OPEN
            elif self.dist1 < self.min_open_dist:
               self.door_state = INIT_OPEN # also confusing, we'll go to open
            elif self.dist2 < self.min_open_dist:
                # stay in this state; maybe we missed the dist2 close in the last cycle
                pass
            else: # neither
                self.door_state = Door.HOLD_OPEN
                
        elif self.door_state == Door.HOLD_OPEN:
            if self.dist1 < self.min_open_dist and self.dist2 < self.min_open_dist:
                # a little weird, are they coming back in? lets assume so
                self.door_state = Door.PASS_THROUGH_CLOSE
            elif self.dist1 < self.min_open_dist:
                # false alarm? that's the bet
                pass
            elif self.dist2 < self.min_open_dist:
                self.door_state = Door.PASS_THROUGH_CLOSE
                pass
            else: # neither
                # stay here -- we're just open
                pass
        elif self.door_state == Door.PASS_THROUGH_CLOSE:
            if self.dist1 < self.min_open_dist and self.dist2 < self.min_open_dist:
                # stay here until they're clear
                pass
            elif self.dist1 < self.min_open_dist:
                # again stay until they've passed
                pass
            elif self.dist2 < self.min_open_dist:
                pass
            else: # neither
                self.door_state = Door.CLOSED
                door.slow_close(self.min_open_secs)
                
        elif self.door_state == Door.CLOSED:
            if self.dist1 < self.min_open_dist and self.dist2 < self.min_open_dist:
                self.door_state = Door.INIT_OPEN
                door.slow_open()
            elif self.dist1 < self.min_open_dist:
                self.door_state = Door.INIT_OPEN
                door.slow_open()
            elif self.dist2 < self.min_open_dist:
                # assume we trapped someone outside
                self.door_state = Door.INIT_OPEN
                door.slow_open()
            else: # neither
                # keep it closed
                door.slow_close(self.min_open_secs)
        logging.info("Dist1 = {} Dist2 = {} PreState = {} State = {}".format(self.dist1,self.dist2,pre_state,self.door_state))

        
door = MotorDoor()
doorstate = DoorState(door,bus)
try:
    while True:
        doorstate.read_distances()
        doorstate.decide()
        time.sleep(0.2)
finally:
    door.slow_open()

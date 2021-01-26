import pi_servo_hat
import smbus, time
import datetime
import logging

class MotorDoor:
    """A class than handles interactions with a servo motor driving the dog door"""
    def __init__(self,bus=1, motor_slot=0,addr=0x40, open_position=300,closed_position=520,jump_dist=5):
        self.logger = logging.getLogger(__name__)
        self.open_position = open_position
        self.closed_position = closed_position
        self.jump_dist = jump_dist

        self.bus = smbus.SMBus(bus)
        self.addr = addr

        self.rotation_position = self.closed_position
        self.opened_time = datetime.datetime.now().timestamp() - 10000 # something a longish time ago... we really don't know
        self.is_open = True

        ## Setup the motor
        time.sleep(1)
        self.bus.write_byte_data(addr, motor_slot, 0x20) # enables word writes
        time.sleep(.25)
        self.bus.write_byte_data(addr, motor_slot, 0x10) # enable Prescale change as noted in the datasheet
        time.sleep(.25) # delay for reset
        self.bus.write_byte_data(addr, 0xfe, 0x79) #changes the Prescale register value for 50 Hz, using the equation in the datasheet.
        self.bus.write_byte_data(addr, motor_slot, 0x20) # enables word writes
        time.sleep(.5)

        self.slow_close(0)
        
    def slow_open(self):
        if not self.is_open:
            self.logger.info("Opening door")
            for i in range(self.closed_position,self.open_position,-1 * self.jump_dist):
                self.move_to(i)

            self.rotation_position = self.open_position
            self.opened_time = datetime.datetime.now().timestamp()
        else:
            self.move_to(self.open_position) # keep forcing open
        self.is_open = True
        
    def slow_close(self,min_time):
        if self.is_open:
            tm = datetime.datetime.now().timestamp()
            if tm - self.opened_time > min_time:
                self.logger.info("Closing door")
                for i in range(self.open_position,self.closed_position,self.jump_dist):
                    self.move_to(i)
                    time.sleep(0.1)
                self.move_to(self.closed_position)
                self.rotation_position = self.closed_position
                self.is_open = False
            else:
                self.logger.debug("Door not closed due to timeout")
        else:
            self.move_to(self.closed_position) # keep forcing open
        
    def move_to(self,move_to_position):
        #write start and stop to channel
        self.bus.write_word_data(self.addr, 0x06, 0) 
        self.bus.write_word_data(self.addr, 0x08, move_to_position)

if __name__ == "__main__":
            
    door = MotorDoor()
    door.slow_open()
    

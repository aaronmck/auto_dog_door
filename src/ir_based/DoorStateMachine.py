from transitions import Machine
from transitions.extensions.states import add_state_features, Tags, Timeout
import time
import asyncio
from transitions.extensions.states import add_state_features
from transitions.extensions.asyncio import AsyncTimeout, AsyncMachine

import random

class DoorStateMachine(object):

    states = [{'name': 'closed'},
              {'name': 'start_open'},
              {'name': 'outside'},
              {'name': 'coming_in'}]
    # states = ['A', {'name': 'B', 'timeout': 0.2, 'on_timeout': 'to_C'}, 'C']
    def __init__(self, name, door):
        
        self.door_openings = 0

        # Initialize the state machine
        self.machine = Machine(model=self, states=DoorStateMachine.states, initial='closed', queued=True)

        self.machine.add_transition(trigger='front', source='closed', dest='start_open',before='open_door')
        self.machine.add_transition(trigger='back', source='start_open', dest='outside')
        self.machine.add_transition(trigger='back', source='outside', dest='coming_in')
        self.machine.add_transition(trigger='front', source='coming_in', dest='closed',after='close_door')

    def close_door(self):
        door.slow_close(self.min_open_secs)

    def open_door(self):
        door.slow_open()


class DoorStub:
    def __init__(self):
        self.count = 0

    def slow_close(self,count):
        print("CLOSING")

    def slow_open(self):
        print("OPENING")
        
if __name__ == "__main__":
            
    door = DoorStub()
    statem = DoorStateMachine("test",door)
    statem.front()
    print(statem.state)
    time.sleep(10)
    print(statem.state)
    statem.front()
    print(statem.state)
    statem.back()
    time.sleep(10)
    print(statem.state)
    statem.back()
    print(statem.state)
    statem.front()
    print(statem.state)

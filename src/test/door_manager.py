from scanner import *
from motor_door import *
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--logfile', help='the log file to write to',required=True)
parser.add_argument('--device', help='the bluetooth MAC address to watch',required=True)
parser.add_argument('--threshold', help='the rssi threshold to open the door',required=True)

args = parser.parse_args()


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Manager:
    def __init__(self,door,scanner,device_address,buffer_size,rssi_threshold,min_open_seconds,logfile):
        self.logger = logging.getLogger(__name__)
        self.door = door
        self.scanner = scanner
        self.scan_buffer = [-90] * buffer_size # a very poor connection
        self.logfile = logfile
        self.min_open_seconds = min_open_seconds
        self.rssi_threshold = rssi_threshold
        
    def callback(self,device):
        self.logger.debug("DEV = {}  RSSI = {}".format(device.addr, device.rssi))
        self.scan_buffer = self.scan_buffer[1:len(self.scan_buffer)]
        self.scan_buffer.append(device.rssi)
        avg = float(sum(self.scan_buffer))/float(len(self.scan_buffer))
        logging.info("DEV = {}  RSSI = {}  Average = {}  DOOR_OPEN = {}".format(device.addr, device.rssi,avg,door.is_open))
        logfile.write("DEV = {}  RSSI = {}  Average = {}  DOOR_OPEN = {}".format(device.addr, device.rssi,avg,door.is_open))
            
        if avg < self.rssi_threshold:
            door.slow_close(self.min_open_seconds)
        else:
            door.slow_open()


logfile=open(args.logfile,"w")

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""Dog door monitor v1""")

rssi_threshold = int(args.threshold)
rssi_buffer_size = 1
scan_spacing_in_secs = 0.5
seconds_door_stays_open = 30

epoch = datetime.datetime.utcfromtimestamp(0)

door = MotorDoor()
scanner = BluetoothScanner(scan_spacing_in_secs)
scanner.add_target(args.device)
manager = Manager(door,scanner,args.device,rssi_buffer_size,rssi_threshold,seconds_door_stays_open,logfile)
while True:
    scanner.scan_and_callback(manager.callback)

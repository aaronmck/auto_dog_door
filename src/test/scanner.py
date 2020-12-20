from bluepy.btle import Scanner
import pi_servo_hat
import smbus, time
import datetime
import logging

class BluetoothScanner:
    def __init__(self,scan_freq):
        self.logger = logging.getLogger(__name__)
        self.scanner = Scanner()
        self.targets = []
        self.scan_freq = scan_freq
        
    def scan_and_callback(self,callback_with_device):
        devices = self.scanner.scan(self.scan_freq)
    
        for device in devices:
            if device.addr in self.targets or len(self.targets) == 0:
                self.logger.debug("Hit on target {}, launching callback".format(device.addr))
                callback_with_device(device)

    def add_target(self,target):
        logger.info("Adding target {}".format(target))
        self.targets.append(target)


        
if __name__ == "__main__":
    
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info("""Dog door monitor v1""")

    def callback(device):
        logging.info("DEV = {}  RSSI = {}".format(device.addr, device.rssi))

        
    scanner = BluetoothScanner(1.0)
    while True:
        scanner.scan_and_callback(callback)

from temperature_controller.ctc100 import CTC100, Channel
from typing import List
from temperature_controller.serial_utils import get_com_ports
import traceback

WHITELISTED = ['COM6']

class CTC100Manager:
    controllers: List[Channel] = []
    sensors: List[Channel] = []
    ctc100s: List[CTC100] = []

    def __init__(self):
        self.detect_ctc100s()

    def detect_ctc100s(self):
        # TODO make logging
        print("CTC100 Manager: Detecting Devices")
        com_ports = get_com_ports()
        # com_ports = [x for x in com_ports if x in WHITELISTED]
        #com_ports.remove('COM7')
        #com_ports.remove('COM3')
        print(com_ports)
        for port in com_ports:
            try:
                c = CTC100(port)
                print(f"CTC100 Manager: device on {port} is a CTC100.")
                self.controllers += c.controllers
                self.sensors += c.sensors
                self.ctc100s.append(c)
            except AssertionError:
                # traceback.print_exc()
                print(f"CTC100 Manager: Device on port {port} does not seem to be a CTC100")

        self.controllers = sorted(self.controllers, key=lambda x: x.name)
        self.sensors = sorted(self.sensors, key=lambda x: x.name)

    def summary(self):
        return f"CTC100 Manager with:\n\t{len(self.ctc100s)} CTC100s containing\n" \
               f"\t{len(self.controllers)} controllers\n" \
               f"\t{len(self.sensors)} sensors"

    def __str__(self):
        return self.summary()


global_ctc_100_manager = CTC100Manager()


if __name__ == "__main__":
    print(get_com_ports())
    print(global_ctc_100_manager.ctc100s)
    print(global_ctc_100_manager.controllers)
    print(global_ctc_100_manager.sensors)
    print(global_ctc_100_manager)

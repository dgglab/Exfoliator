from temperature_controller.ikaret import IKARET, Channel
from typing import List
from temperature_controller.serial_utils import get_com_ports
import traceback

WHITELISTED = ['COM5','COM6']

class IKARETManager:
    controllers: List[Channel] = []
    sensors: List[Channel] = []
    ikarets: List[IKARET] = []

    def __init__(self):
        self.detect_ikaret()

    def detect_ikaret(self):
        # TODO make logging
        print("IKARET Manager: Detecting Devices")
        com_ports = get_com_ports()
        com_ports = [x for x in com_ports if x in WHITELISTED]
        print(com_ports)
        for port in com_ports:
            try:
                c = IKARET(port)
                print(f"IKARET Manager: device on {port} is an IKA RET.")
                self.controllers += c.controllers
                self.sensors += c.sensors
                self.ikarets.append(c)
            except AssertionError:
                # traceback.print_exc()
                print(f"IKA RET Manager: Device on port {port} does not seem to be an IKA RET.")

        self.controllers = sorted(self.controllers, key=lambda x: x.name)
        self.sensors = sorted(self.sensors, key=lambda x: x.name)
    
        

    def summary(self):
        return f"IKA RET Manager with:\n\t{len(self.ikarets)} IKA RETs containing\n" \
               f"\t{len(self.controllers)} controllers\n" \
               f"\t{len(self.sensors)} sensors"

    def __str__(self):
        return self.summary()


global_ikaret_manager = IKARETManager()


if __name__ == "__main__":
    print(get_com_ports())
    print(global_ikaret_manager.ikarets)
    print(global_ikaret_manager.controllers)
    print(global_ikaret_manager.sensors)
    print(global_ikaret_manager)

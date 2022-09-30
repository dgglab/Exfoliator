import serial
from typing import Optional, Callable, Dict, List

from PyQt5.QtCore import QMutex

from temperature_controller.table_utils import DDict

def parse_list(list_response: str, remove_periods: bool = True) -> list:
    """
    alarm., Name, Value, Status, Off, Low lmt, Hi lmt, IO type, Plot, Logging, Figures, Stats, Points
    """
    # Break into words and remove surrounding whitespace
    sections = [x.strip() for x in list_response.split(',')]
    # Remove whitespace from inside
    sections = [x.replace(' ', '') for x in sections]
    # Lowercase words
    sections = [x.lower() for x in sections]
    # Remove periods
    if remove_periods:
        sections = [x.strip('.') for x in sections]
    return sections





class IKARET(DDict):
    def __init__(self, port):
        super().__init__()
        self.port = port
        
        print('initializing hot plate')
        self.serial_connection = serial.Serial(port=port, baudrate=9600, timeout=1)
        self.mutex = QMutex()
        self.send('START_1')
        self.send('START_90')
    def send(self, msg):
        if not type(msg) is bytes:
            msg = bytes(msg, 'utf-8')
        self.serial_connection.write(msg + b'\r\n')

        try:
            response = self.serial_connection.read_until(b'\r\n').decode('utf-8').strip()
        except UnicodeDecodeError:
            print(f"UNICODE DECODE ERROR: {msg}")
            response = ''
        # print(response)
        return response
    
    def get_weight(self):
        weight=self.send('IN_PV_90')
        length=len(weight)
        weight=weight[:length-2]
        return weight
    def tare(self):
        self.send('START_90')
    def get_temp(self,flag):
        if flag==0:
            temp=self.send('IN_PV_2')
        if flag==1:
            temp=self.send('IN_PV_1')
        length=len(temp)
        temp=temp[:length-1]
        return temp
    def set_temp(self,goal,flag):
        if flag==0: #defaults to hot plate
            self.send(f'OUT_SP_2 {goal}')
            print("trace")
        if flag==1:
            self.send(f'OUT_SP_1 {goal}')
 
    def close(self):
        self.serial_connection.close()





class EmulatedIKARET(IKARET):
    def __init__(self, *args, **kwargs):
        self.channels = {
            x: Channel(x, lambda str: f"Channel-{x}: {str}") for x in ['c1', 'c2', 'c3']
        }

    def send(self, msg):
        print(f"[Eumulator] send msg {msg}")

# Commands
# pid.setpoint=<value>
# pid.rampt=<value>
# pid.ramp=<value>
# pid.p=<gain>
# pid.i=<integral>
# pid.d=<derivative>

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        com = sys.argv[1]
    else:
        com = 'COM7'
    c = IKARET(com)
    from IPython import embed
    embed()


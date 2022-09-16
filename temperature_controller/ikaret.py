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


class Channel:
    def __init__(self, name: str, send_fn: Callable[[str], str], parent):
        # Pass in function
        self.name = name
        self.parent = parent
        self.send = send_fn
        self.pid: Optional[Channel] = None
        self.mutex = self.parent.mutex
        self.send('START_1')
        self.send('START_90')
        print(self.send('IN_PV_90'))
    @property
    def value(self):
        return self.send('value?')

    @property
    def pid_raw(self):
        if 'pid' in self.list():
            return parse_list(self.send('pid.list?'))
        else:
            return None

    def list(self):
        return parse_list(self.send('list'))

    def __repr__(self):
        return f"SRS:{self.parent.port}-{self.name}"


class IKARET(DDict):
    def __init__(self, port):
        super().__init__()
        self.channels: Dict[str, Channel] = {}
        self.port = port
        
        print('initializing hot plate')
        super().__init__()
        self.channels: Dict[str, Channel] = {}
        self.port = port
        self.serial_connection = serial.Serial(port=port, baudrate=9600, timeout=1)
        #try:
         #   self._confirm_valid()
        #except AssertionError as e:
        #    self.serial_connection.close()
        #    raise e
        #else:
        self._get_channels()

        self.controllers = [c for c in self.channels.values() if c.pid]
        self.sensors = [c for c in self.channels.values() if not c.pid]
        self.mutex = QMutex()
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
    

    #def _confirm_valid(self):
        #"""
        #'CTC100 Cryogenic Temperature Controller, version 4.40, S/N 153476'
        #"""
        #output = self.send('description?')
        #assert "CTC100" in output, f"Failed verification check, description does not look valid: '{output}'"
    def get_weight(self):
        weight=self.send('IN_PV_90')
        return weight
    def get_temp(self,flag):
        if flag==0:
            temp=self.send('IN_PV_2')
        if flag==1:
            temp=self.send('IN_PV_1')
        return temp
    def set_temp(self,goal,flag):
        if flag==0: #defaults to hot plate
            self.send('OUT_SP_2 {goal}')
        if flag==1:
            self.send('OUT_SP_1 {goal}')
    def _get_chan_send(self, channel):
        def chan_send(msg):
            return self.send(f"{channel}.{msg}")

        return chan_send

    def _get_channels(self) -> None:
        # Retrieve list of channel names
        channel_names = parse_list(self.send('channel.list'))
        for name in channel_names:
            self.channels[name] = Channel(name, self._get_chan_send(name), self)

        for name, channel in self.channels.items():
            pid_raw = channel.pid_raw
            if pid_raw:
                input_channel_name = channel.send('pid.input?').replace(' ', '').lower()
                if input_channel_name != 'unselected':
                    print(channel.name, 'has pid input', input_channel_name)
                    input_channel = self.channels[input_channel_name]
                    input_channel.pid = channel
                else:
                    print(channel.name, ' has unselected pid')

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


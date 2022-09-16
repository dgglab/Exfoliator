from typing import Dict, List
import logging

from PyQt5.QtWidgets import QWidget, QGridLayout, QAbstractItemView, QHeaderView, QTableView, QTextEdit, QVBoxLayout, \
    QPushButton, QApplication, QDialog

from temperature_controller.controller_table import TemperatureControllerTableModel, TemperatureControllerTable
from temperature_controller.controller_table import ControllerTableRow, TemperatureControllerTableView, \
    TemperatureControllerTableDelegate, \
    ControllerTableRowControlButtons, ConfigureRowsDialog
from temperature_controller.poller import PollResponse, ChannelPoller
from temperature_controller.log_widget import logger, log_editor
from temperature_controller.sensor_table import TemperatureSensorTable, SensorTableRow
import serial
from typing import Optional, Callable, Dict, List

from PyQt5.QtCore import QMutex

from temperature_controller.table_utils import DDict
from typing import List
from temperature_controller.serial_utils import get_com_ports
import traceback

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

ALLOWED_CHANNEL_NAMES = [f"p{x}" for x in range(6)]


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
class TemperatureDashboard(QWidget):
    """
    Dashboard for system temperature controllers and sensors.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ikaret=IKARET()
        self.ikaret.send('START_1')
        self.init_ui()

    def init_ui(self):
        sensors = [x for x in global_ikaret_manager.sensors if x.name.lower().startswith("bot-") or x.name.lower() in [
            'festival', 'of', 'vdw', 'stacking', 'aaa', 'bbb', 'ccc'
        ]]
        self.temperature_sensor_table = TemperatureSensorTable(sensors)

        controllers = global_ikaret_manager.controllers
        self.temperature_controller_table = TemperatureControllerTable(controllers)


        self.log_display = self.build_log_display()
        self.dashboard_buttons = self.build_dashboard_buttons()

        main_layout = QGridLayout(self)
        main_layout.addWidget(self.temperature_controller_table, 0, 0, 1, 3)
        main_layout.addWidget(self.temperature_sensor_table, 1, 0)
        main_layout.addWidget(self.log_display, 1, 1)
        main_layout.addWidget(self.dashboard_buttons, 1, 2)
        self.setLayout(main_layout)


    def configure_controllers(self):
        dialog = ConfigureRowsDialog(parent=self)
        logger.info("Configure")

    def hold_all_controllers(self):
        logger.info("Hold all")

    def switch_all_controllers_off(self):
        # TODO: call off on all the controllers.
        logger.info("Switching all off")

    def build_log_display(self) -> QWidget:
        log_display = QTextEdit()
        log_display.setReadOnly(True)
        log_editor.connect_editor(log_display)
        logger.addHandler(log_editor)
        logger.info("Startup")
        return log_display

    def printfunc(self,arg):
        print(arg)
    def build_dashboard_buttons(self) -> QWidget:
        buttons = QWidget(self)
        buttons_layout = QVBoxLayout(buttons)
        configure_button = QPushButton("Configure Rows")
        configure_button.setEnabled(False)
        configure_button.clicked.connect(self.configure_controllers)
        hold_all_button = QPushButton("Hold All")
        hold_all_button.setEnabled(False)
        hold_all_button.clicked.connect(self.hold_all_controllers)
        newbutton=QPushButton("Test New Button")
        newbutton.setEnabled(True)
        newbutton.clicked.connect(IKARET.get_weight())
        switch_off_all_button = QPushButton("Switch Off All")
        switch_off_all_button.setEnabled(False)
        switch_off_all_button.clicked.connect(self.switch_all_controllers_off)
        buttons.setLayout(buttons_layout)
        for b in [configure_button, hold_all_button, switch_off_all_button,newbutton]:
            buttons_layout.addWidget(b)
        return buttons


if __name__ == "__main__":
    qApp = QApplication([])
    t = TemperatureDashboard()
    t.setGeometry(100, 100, 1080, 720)
    t.show()
    t.setWindowTitle('Temp')
    qApp.exec()


import dataclasses
import time
from typing import Optional, List

from PyQt5.QtCore import QThread, pyqtSignal, QMutexLocker

from recordclass import RecordClass

# Model the state and state transisions of a controller device

@dataclasses.dataclass
class StatusNode:
    value: str
    parent = None
    children = []

    def __repr__(self):
        return f"{self.__class__}-{str(self)}"

    def __str__(self):
        """ Recurse up the tree """
        cur = self
        chain = []
        while cur:
            chain.append(cur.name)
            cur = cur.parent
        return chain[::-1]




class ConnectionStatuses:
    NOT_CONNECTED = "Not Connected"
    CONNECTED = "CONNECTED"
    ON = "ON"
"""
CONNECTED: was able to pair this logical device with an underlying device.
CONNECTED_EMULATOR: (testing only) was able to pair this logical device with an underlying emulated device.
NOT CONNECTED: was unable to associate this logical device with an underlying device

CONTROLLER_ON: Controller is enabled
CONTROLLER_OFF: Controller is not enabled. Sensing only

(Controller OFF) STANDBY: Controller is not on, temperature is free-falling to room temp.
(Controller ON) STABLE: temperature is being held at constant temperature
(Controller ON) RAMPING: temperature is moving towards a target value

What we have here is a logic tree. How do you capture the logic tree in a set of states?
* Is this device connected? If no, then nothign to do. If yes, then 

Think of your state as a path through the tree:
/not_connected
/connected/off/standby
/connected/on/stable
/connected/on/ramping
"""


class ControllerChannel(RecordClass):
    state: str
    name: str
    value: float
    setpoint: float
    ramp_rate: float
    working_setpoint: float
    current_output: float
    max_output: float


@dataclasses.dataclass
class PollResponse:
    name: str  # channel name
    value: float
    pid_on: Optional[bool] = False
    setpoint: Optional[float] = None
    ramp_rate: Optional[float] = None
    working_setpoint: Optional[float] = None
    current_output: Optional[float] = None
    max_output: Optional[float] = None


class ChannelPoller(QThread):
    updateReady = pyqtSignal(dict)

    def __init__(self, channels: List[ControllerChannel], poll_frequency_s: float=0.25, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = channels
        self.poll_frequency_s = poll_frequency_s

    def run(self) -> None:
        while True:
            try:
                values = {}
                for channel in self.channels:
                    with QMutexLocker(channel.parent.mutex):
                        pid = channel.pid
                        if pid:
                            values[channel.name] = PollResponse(
                                channel.name,
                                float(channel.value),
                                pid.send('pid.mode?') == 'On',
                                float(pid.send('pid.setpoint?')),
                                float(pid.send('pid.ramp?')),
                                float(pid.send('pid.rampt?')),
                                float(pid.send('value?')),
                                float(pid.send('hilmt?'))
                            )
                        else:
                            values[channel.name] = PollResponse(
                                channel.name,
                                float(channel.send('value?'))
                            )
                self.updateReady.emit(values)
                time.sleep(self.poll_frequency_s)
            except Exception:
                import traceback
                traceback.print_exc()

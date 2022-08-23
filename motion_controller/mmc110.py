import dataclasses
import re
from typing import List, Dict, Any
from pymmc_commands import COMMANDS

import serial

N_BUFFER_CLEAR_BYTES = 100
###07/28/22 change -- getting rid of 'TLN' -- problem with axis 9
axis_parameters = [
    'AMX',
    'VMX',
    'JAC',
    'TLP',
    'REZ',
    'ENC',
    'FBK',
    'DBD',
    'PID',
    'EPL',
    'ACC',
    'VEL',
]

@dataclasses.dataclass
class Axis:
    number: int
    version: str
    parameters: Dict[str, Any] = dataclasses.field(default_factory=dict)


class MMC110:
    """
    Product page:
        https://micronixusa.com/product/yvwR8n/new-products/modular-motion-controller-mmc-110
    manual:
        https://micronixusa.com/product/download/yvwR8n/universal-document/jVW4zX

    Requires FTDI drivers to be installed in order for visibility to OS. https://ftdichip.com/drivers/vcp-drivers/

    Notes
    * whitespace and case ignored in commands.
    * either send `\n\r` or `\r` to terminate writes. (page 5-11 in the manual)
    * Note that MMC110 the 0x0A [\n] and 0x0D for [\r], this is the same as python3's b'\n' and b'\r'

    """
    baudarate = 38400
    stopbits = serial.STOPBITS_ONE
    parity = serial.PARITY_NONE
    databits = serial.EIGHTBITS  # nb: pyserial calls this bytesize
    # Also, No handshake.
    read_timeout = 0.1 #0.75 -> 0.1
    write_timeout = 0.25
    write_terminating_symbol = b'\n\r'
    read_terminating_symbol = b'\n\r'
    confirm_prompt_template = "{axis}VER?"
    confirm_response_re = "#MMC-.*"
    axes: Dict[int, Axis] = {}
    axis_limit = 11  # or 16? main url says 6, manual says 16. Maximum possible axes in a single mmc110 stack

    def __init__(self, port):
        self.serial_connection = serial.Serial(port=port,
                                               baudrate=MMC110.baudarate,
                                               bytesize=MMC110.databits,
                                               parity=MMC110.parity,
                                               stopbits=MMC110.stopbits,
                                               timeout=MMC110.read_timeout,
                                               write_timeout=MMC110.write_timeout,
                                               )
        self.clear_buffer()
        self.get_status_byte()
        self.detect_axes()
        assert self.axes, "No axes found on this controller. This appears to not be a valid device"
        self.get_axis_params()
        self.print_axes()

    def get_status_byte(self):
        """
        Return MMC110 status byte
        TODO: link to docs
        """


    def get_axis_params(self):
        for axis in self.axes.values():
            for param in axis_parameters:
                cmd = f"{axis.number}{param}?"
                axis.parameters[param] = self.send(cmd)

    def clear_buffer(self):
        print(f"clearing buffer by reading {N_BUFFER_CLEAR_BYTES}")
        print("Buffer Contents: ", self.serial_connection.read(N_BUFFER_CLEAR_BYTES))

    def send(self, msg: str):
        """
        Assumes message strings are utf-8 encoded.

        TODO: add timeout errors. this should raise an exception. Monadic return.
        """
        if not type(msg) is bytes:
            msg = bytes(msg, 'utf-8')
        print("=>", msg.decode('utf-8'))
        self.serial_connection.write(msg + MMC110.write_terminating_symbol)
        response = self.serial_connection.read_until(MMC110.read_terminating_symbol).decode('utf-8').strip()
        print("<=", response)
        return response


    def detect_axes(self, early_stop_n=10):
        """
        TODO: Fill out below, do this right
        The MMC110 protocol for detecting axes is to iterate through list of axes.

        Loop through and check for versions on axes.
        Set default axis limit to be 2 misses then stop.
        """
        n_misses = 0
        for i in range(1, MMC110.axis_limit):
            response = self.send(MMC110.confirm_prompt_template.format(axis=i))
            if re.search(MMC110.confirm_response_re, response):
                self.axes[i] = Axis(i, response)
            else:
                n_misses += 1
                if n_misses == early_stop_n:
                    break
        self.print_axes()

    def print_axes(self):
        for a in self.axes.values():
            print(a)


    def move_rel(self, axis_number: int, amount: float):
        # TODO: commands should be enum.
        self.send(self.build_command(axis_number, 'MVR', (amount,)))

    def move_abs(self, axis_number: int, amount: float):
        # TODO: commands should be enum.
        self.send(self.build_command(axis_number, 'MVA', (amount,)))


    def build_command(self, axis_number: int, command: str, parameters: tuple = (), query=False):
        # TODO: check if axis is valid
        if not command in COMMANDS.keys():
            raise RuntimeError("Invalid Command")
        if query:
            command_str = f"{axis_number}{command}?"
        else:
            param_str = ",".join(parameters)
            command_str = f"{axis_number}{command}{param_str}"
        return command_str

    def get_axis(self, axis_number: int) -> Axis:
        return self.axes[axis_number]

    def close(self):
        self.serial_connection.close()
if __name__ == "__main__":
    MMC110("COM4")















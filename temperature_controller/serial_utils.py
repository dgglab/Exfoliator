from typing import List
import serial
import serial.tools.list_ports
import serial.tools.list_ports_common


def get_com_ports_info() -> List[serial.tools.list_ports_common.ListPortInfo]:
    """
    List com ports on the system
    See https://pyserial.readthedocs.io/en/latest/tools.html#module-serial.tools.list_ports
    and
    https://github.com/pyserial/pyserial/blob/master/serial/tools/list_ports_common.py
    """
    return serial.tools.list_ports.comports()


def get_com_ports() -> List[str]:
    return [x.device for x in get_com_ports_info()]

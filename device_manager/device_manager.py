import enum
from typing import Dict
from recordclass import RecordClass

class DeviceStatus(enum.Enum):
    CONNECTED = enum.auto()
    NOT_CONNECTED = enum.auto()
    ERROR = enum.auto()

class DeviceFamily(enum.Enum):
    CAMERA = "camera"
    TEMPERATURE = "temperature controller"
    MOTION = "motion controller"


class Device(RecordClass):
    family: DeviceFamily
    com_port: str
    status: DeviceStatus = DeviceStatus.NOT_CONNECTED


class DeviceManager:
    instance = None
    devices = Dict[str: Device] = {}

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def __init__(self):
        if self.instance:
            raise RuntimeError("Attempted to instantiate singleton object. Use DeviceManager.get_instance() instead")

    def get(self, key: str):
        return self.devices.get(key)

    def list_devices(self):
        return list(self.devices.keys())

    def detect_devices(self):
        """ use serial scan to understand connected devices on COM ports """
        self.devices = {
            'CTC100': Device(
                DeviceFamily.MOTION,
                com_port="COM5",
                status=DeviceStatus.CONNECTED
            )
        }

    def get_devices_by_family(self, family: DeviceFamily):
        return [x for x in self.devices.values() if x.family == family]

    def get_devices_by_type(self, _type):
        return [x for x in self.devices.values() if type(x) is type]

    @property
    def cameras(self):
        return self.get_devices_by_family(DeviceFamily.CAMERA)
    @property
    def temperature_controllers(self):
        return self.get_devices_by_family(DeviceFamily.TEMPERATURE)
    @property
    def motion_controllers(self):
        return self.get_devices_by_family(DeviceFamily.MOTION)








global_device_manager = DeviceManager.get_instance()

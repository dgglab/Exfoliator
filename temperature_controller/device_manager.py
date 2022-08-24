# Cheating. Putting a temporary copy of device manager here. To be merged with device manager module later.

"""
Device manager is a container class for "Instruments". Instruments are anything you can connect to the computer,
whether that be a camera, SRS CTC100, or MMC110, etc. Instruments multiplex multiple "Devices". Devices may be
Channels (in the case of CTC100) or Axes (in the case of MMC100) and so forth.

The goal is to provide some virtual addressing to abstract away the multiplexing. So the rough procedure the DM follows
is (a) scan for and detect instruments, (b) determine the devices that exist on the instrument, (c) build an index
of these devices so they can be used throughout the rest of the system.

The Device Manager maintains state globally of instruments and devices of the system. This state is accessible to other
modules by importing the singleton device manager object from this module.

Each instrument is responsible for implementing its own "poll" function that updates the Device manager's global state
pertaining to the Devices that the Instrument contains. For example, there will be a CTC100 poll function which updates
the state of all the channels on that device.

Updating all devices for an instrument within a single poll function allows for improved efficiency in communicating
with the devices, since the same request to the device may multiplex state for all its channels, rather than requiring
a single request for each channel.

The device manager's state is stored in the main pyqt gui thread. Poll functions run in separate QThreads to update
the state in the main thread. Access to this state by gui Widgets is consistent and threadsafe as updates to the main
thread state are performed by the main thread reading from a queue.
"""
# import typing
# from temperature_controller.serial_utils import get_com_ports
# from temperature_controller.ctc100 import CTC100, Channel
# from PyQt5.QtCore import QObject
#
# INSTRUMENT_TYPES = [
#     CTC100
# ]
#
#
# class DeviceManager(QObject):
#     """
#     Global container for Instruments and Devices
#     """
#     WHITELISTED_PORTS = "COM3"
#     port_to_instrument_index: dict[str, typing.Any] = {}  # index to instruments
#     instrument_type_to_instruments_index = dict[str, typing.List[str]]
#     instruments: typing.List[typing.Any] = []
#
#     def __int__(self, *args, **kwargs):
#         """ No Initialization work happens. Possibly this class may be set as singleton by using a classmethod.
#         Instead, we use the global object import pattern, see object instantiation bellow.
#         """
#         self.instrument_type_to_instruments_index = {k: [] for k in INSTRUMENT_TYPES}
#
#     def detect_devices(self):
#         """
#         Detect devices connected to the computer. Currently this only supports serial devices and cameras detectable
#         by the Windows device manager.
#
#         There's probably a way to use VID/PID of the COM ports to detect which instrument type is on each port...
#         but for now just try and see what works.
#         """
#         com_ports = [x for x in get_com_ports() if x in self.WHITELISTED_PORTS]
#
#         for port in com_ports:
#             matched = False
#             for instrument_type in INSTRUMENT_TYPES:
#                 try:
#                     i = instrument_type(port)
#                 except TypeError:
#                     print(f"Instrument on {port} is apparently not a {instrument_type.__name__}")
#                 else:
#                     print(f"Detected {instrument_type.__name__} on port {port}")
#                     self.port_to_instrument_index[port] = i
#                     self.instrument_type_to_instruments_index[instrument_type].append(i)
#                     self.instruments.append(i)
#                     matched = True
#                     break
#             if not matched:
#                 print(f"WARNING: Could not determine instrument on port {port}")
#
#     @property
#     def temperature_controllers(self) -> Channel:
#         resp = []
#         for i in self.instrument_type_to_instruments_index[CTC100]:
#             i: CTC100
#             resp += i.controllers
#         return resp
#
#     @property
#     def temperature_sensors(self) -> Channel:
#         resp = []
#         for i in self.instrument_type_to_instruments_index[CTC100]:
#             i: CTC100
#             resp += i.sensors
#         return resp
#
#
#
#
#
# GLOBAL_DEVICE_MANAGER = DeviceManager()
#
# if __name__ == "__main__":
#     GLOBAL_DEVICE_MANAGER.detect_devices()
#     print(GLOBAL_DEVICE_MANAGER.instrument_index)
#

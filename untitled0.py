# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 11:23:29 2022

@author: GGG-EXFOLIATOR
"""

from ctypes import cdll
# import pythonnet
# pythonnet.load()
# import clr
# clr.AddReference("C:\\Users\\GGG-EXFOLIATOR\\Documents\\GitHub\\Exfoliator\\futekusb\\USB_IronPython\\USB Example Python\\FUTEK_USB_DLL.dll")
futek=cdll.LoadLibrary("./futekusb/futek.devices/x64/FUTEK.Devices.dll")
futek2=cdll.LoadLibrary("./futekusb/futek.devices/x64/FUTEK_USB_DLL.dll")


futek2.


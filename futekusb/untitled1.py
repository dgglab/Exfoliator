# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 12:15:23 2022

@author: GGG-EXFOLIATOR
"""
import serial
import serial.tools.list_ports as port_list
ports = list(port_list.comports())
for p in ports:
    print (p)
FutekPort = serial.Serial(port="COM6", baudrate=2000000,timeout=0.02)#, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
serialString = ""  # Used to hold data coming over UART
print('Reading')
while 1:
    # Wait until there is data waiting in the serial buffer
    
    if FutekPort.in_waiting < 4:
         FutekPort.reset_input_buffer()
    else:
        # Read data out of the buffer until a carraige return / new line is found
        serialString = FutekPort.readline()
        print('ss',serialString)
        # Print the contents of the serial data
        try:
            ss2=serialString.decode("Ascii")
            ss2=str(ss2)
            ss3=ss2[0:8]
            print('ss3',ss3)
        except:
            pass
print('Reading')

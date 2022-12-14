from PyQt5 import QtCore, QtWidgets as QtW
from PyQt5.QtCore import QTimer
import time
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import QSizePolicy
import temperature_controller.ikaret as ika
import futekusb.FUTEKUSB as fusb
import threading
import sys
import serial

IKA = ika.IKARET("COM5")
FutekPort = serial.Serial(port="COM6", baudrate=2000000,timeout=0.02)#, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
FutekString = ""  # Used to hold data coming over UART

class MotionWindow(QtW.QWidget):
    start_video_signal = QtCore.pyqtSignal(object)
    save_frame_signal = QtCore.pyqtSignal(object)
    stop_video_signal = QtCore.pyqtSignal(object)
    def __init__(self, logger):
        super().__init__()
        self.queue_manager = Queue_Manager()
        self.queue_manager.position_signal.connect(self.update_position)
        self.motors = {}
        self.plates={}
        self.plate_connected = False
        self.motor_connected = False

        self.axis_to_motor = {}

        self.num_to_axis = {1:'Sample X', 2: 'Sample Y', 3: 'Sample Z'}

        self.stock_labels = ['Axis', 'Indexed?', '', '', 'Position', 'Unit', '', 'Move to', '', 'Move by', '', '',
                             'Feedback mode']

        self.axis_display_order = [1,2,3]
        self.axis_display_label = {}
        self.axis_display_unit = ['(mm)' if num <4 else '(deg)' for num in
                                  self.axis_display_order]

        self.available_axes = []

        for i in range(0, len(self.axis_display_order)):
            self.axis_display_label[self.axis_display_order[i]] = self.axis_display_unit[i]

        self.labels = {}
        self.buttons = {}
        self.lineEdits = {}
        self.lists = {}
        self.boxes = {}
        self.globalweight=0
        self.logger = logger
        self.recordings = {}

        self.active_loop = False

        self.GUI_Elements()
        self.hp_timer = QTimer()
        self.hp_timer.timeout.connect(self.on_hp_poller_timeout)
        self.start_hp_poller()
        path="C:/Users/GGG-EXFOLIATOR/Documents/GitHub/Exfoliator/Coefficients.txt"
        print('Loading Coefficients')
        self.coefflist=np.loadtxt(path,dtype=float,delimiter=', ', skiprows=12,usecols=(1),unpack=True)
        print(self.coefflist)

    def start_hp_poller(self):
        self.hp_timer.start(200)
        
    def on_hp_poller_timeout(self):
        self.globalweight=float(weight_thread.get_weight(self))
        self.update_pos2(1)
        self.update_pos2(2)
        self.update_pos2(3)
        #print(self.globalweight)
    # def get_weight(self,saveflag=0):
    #     #weight=IKA.get_weight()
    #     bytecount=0
    #     while bytecount < 4:
    #         FutekPort.reset_input_buffer()
    #         bytecount=FutekPort.in_waiting
    #     bytecount=0
    #     if 1:
    #         serialString = FutekPort.readline()
    #         #print(serialString)
    #         serialString2=serialString.decode("Ascii") #weight in pounds
    #         #print(type(serialString2),serialString2)
    #         weightlbs=float(serialString2[0:7])
    #         lbstogram=-1*453.592 #compression is positive
    #         weight=round(weightlbs*lbstogram,1)
    #         print(weight)
    #         if saveflag==1:
    #             now=time.localtime(time.time())
    #             month=now.tm_mon
    #             day=now.tm_mday
    #             year=now.tm_year
    #             name=str(year)+'_'+str(month)+'_'+str(day)+' Force Log.txt'
    #             now2=time.mktime(time.strptime(str(day)+' '+str(month)+' '+str(year), "%d %m %Y"))
    #             deltime=str(time.time()-now2)
    #             f=open(name,'a+')
    #             weight2=str(round(float(weight),2))
    #             writestr=str(deltime+' '+weight2+'\n')
    #             f.write(writestr)
    #             f.close()
    #         if abs(float(weight))<10000:# and float(weight)>-3000:
    #             return weight
    #         else:
    #             print('Weight fault!',weight)
    #             #if float(weight)<=-3000:
    #                 #return -0.5
    #             if abs(float(weight))>=10000:
    #                 return 0.5
    def get_ret_weight(self,start):
        weight=IKA.get_weight()
        name=str(int(start))+' Force Log.txt'
        deltime=str(time.time()-start)
        f=open(name,'a+')
        weight2=str(int(float(weight)))
        writestr=str(deltime+' '+weight2+'\n')
        f.write(writestr)
        f.close()
        return weight
    def get_temp(self,flag):
        return IKA.get_temp(flag)
    def set_temp(self,goal,flag):
        return IKA.set_temp(goal,flag)
    def tare(self):
        #IKA.tare()
        bytecount=0
        while bytecount < 4:
            FutekPort.reset_input_buffer()
            bytecount=FutekPort.in_waiting
        bytecount=0
        if 1:
            serialString = FutekPort.readline()
            serialString2=serialString.decode("Ascii") #weight in pounds
            tarew=0
            if len(serialString2)>2:
                    weightlbs=float(serialString2[0:7])
                    lbstogram=-1*453.592 #compression is positive
                    tarew=weightlbs*lbstogram
            return tarew
            print('Taring',tarew)
    def sleepytare(self):
        IKA.tare()
        print('Taring')
        timer=self.coefflist[3]
        sleep_thread.sleepfunc(self,timer)
    
    def connect_motor(self, connection_msg):
        print(connection_msg)
        if connection_msg[0] == 'IKA':
            self.plates[connection_msg[0]] = connection_msg[1]
            print('Plate connected!',connection_msg[0])
        if connection_msg[0] == 'MMC1':
            self.motors[connection_msg[0]] = connection_msg[1]
            for axis in self.motors[connection_msg[0]].axes.values():
                self.available_axes.append(axis.number)
                print('Motors Connected!',connection_msg[0], axis.number)
                self.axis_to_motor[axis.number] = connection_msg[1]
                self.buttons[f'Home {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'Zero {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'Stop {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'+ {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'- {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons['Motor On'].setEnabled(True)
                self.buttons['Motor Off'].setEnabled(True)
                # Homing for these disabled for safety
                if axis.number == 7 or axis.number == 8 or axis.number == 9:
                    self.buttons[f'Home {self.num_to_axis[axis.number]}'].setEnabled(False)
                    self.buttons["Timed Approach"].setEnabled(True)
                    self.buttons['Timed Retract'].setEnabled(True)
                    self.buttons['Stop Loop'].setEnabled(True)
                if axis.number == 7 or axis.number == 8 or axis.number == 9:
                    self.boxes[f'CL {self.num_to_axis[axis.number]}'].setEnabled(False)

            # if 7 in self.available_axes and 10 in self.available_axes:
            #     self.boxes['Microscope -> Sample Z'].setEnabled(True)

            # if 2 in self.available_axes and 3 in self.available_axes and 8 in self.available_axes:
            #     self.boxes['Sample X -> Gonio1'].setEnabled(True)

            # if 4 in self.available_axes and 9 in self.available_axes:
            #     self.boxes['Sample Y -> Gonio2'].setEnabled(True)

            if not self.motor_connected:
                self.motor_connected = True
                self.buttons["Axes Parameters"].setEnabled(True)
                self.buttons["Clear Errors"].setEnabled(True)
                self.buttons["EST Stop"].setEnabled(True)
                self.buttons["Map"].setEnabled(True)
                self.buttons["Jog"].setEnabled(True)
                self.buttons["CMD Line"].setEnabled(True)
                self.boxes['Rec Position'].setEnabled(True)
                self.boxes['Rec Frames'].setEnabled(True)
                self.boxes['Rec Temp'].setEnabled(True)

            self.queue_manager.motors = self.motors
            self.queue_manager.axis_to_motor = self.axis_to_motor
            print('Check', self.axis_to_motor)

            self.init_motor_settings(self.motors[connection_msg[0]].axes.values())

    def init_motor_settings(self, axes):
        for axis in axes:
            self.queue_manager.queue(axis.number, f'{axis.number}POS?')
            self.queue_manager.queue(axis.number, f'{axis.number}FBK0')
            self.queue_manager.queue(axis.number, f'{axis.number}MOT1')
            self.queue_manager.queue(axis.number, f'{axis.number}VEL10')
            #self.queue_manager.queue(axis.number, f'{axis.number}VMX?')

    def GUI_Elements(self):
        self.layout = QtW.QGridLayout(self)

        row_counter = 0
        column_counter = 0
        self.buttons["Axes Parameters"] = QtW.QPushButton("Set Parameters")
        self.buttons["Axes Parameters"].clicked.connect(self.change_parameters)
        self.layout.addWidget(self.buttons["Axes Parameters"], 0, 0, 1, 2)

        self.buttons["Clear Errors"] = QtW.QPushButton("Clear Errors")
        self.buttons["Clear Errors"].clicked.connect(self.clear_errors)
        self.layout.addWidget(self.buttons["Clear Errors"], 0, 2, 1, 2)

        self.buttons["EST Stop"] = QtW.QPushButton("Emergency Stop")
        self.layout.addWidget(self.buttons["EST Stop"], 0, 4, 1, 2)

        self.buttons['Map'] = QtW.QPushButton("Coordinates Map")
        self.layout.addWidget(self.buttons["Map"], 0, 6, 1, 2)

        self.buttons['Jog'] = QtW.QPushButton("Jog")
        self.layout.addWidget(self.buttons["Jog"], 0, 8, 1, 2)

        self.buttons['CMD Line'] = QtW.QPushButton("Command Line")
        self.layout.addWidget(self.buttons["CMD Line"], 0, 10, 1, 2)

        self.buttons['Motor On'] = QtW.QPushButton("Toggle On")
        self.buttons['Motor On'].clicked.connect(lambda state, x=True: self.toggle_motors(x))
        self.layout.addWidget(self.buttons['Motor On'], 0, 12)

        self.buttons['Motor Off'] = QtW.QPushButton("Toggle Off")
        self.buttons['Motor Off'].clicked.connect(lambda state, x=False: self.toggle_motors(x))
        self.layout.addWidget(self.buttons['Motor Off'], 0, 13)

        row_counter += 1
        for i in range(0, len(self.stock_labels)):
            self.layout.addWidget(QtW.QLabel(self.stock_labels[i]), row_counter, i)

        row_counter += 1

        for axis in self.axis_display_order:
            self.layout.addWidget(QtW.QLabel(self.num_to_axis[axis]), row_counter + self.axis_display_order.index(axis),
                                  column_counter)

        column_counter += 1
        for axis in self.axis_display_order:
            self.labels[f'Home Status {self.num_to_axis[axis]}'] = QtW.QLabel('No')
            self.layout.addWidget(self.labels[f'Home Status {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.buttons[f'Home {self.num_to_axis[axis]}'] = QtW.QPushButton('Home')
            self.buttons[f'Home {self.num_to_axis[axis]}'].clicked.connect(lambda state, x=axis: self.home_axis(x))
            self.layout.addWidget(self.buttons[f'Home {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.buttons[f'Zero {self.num_to_axis[axis]}'] = QtW.QPushButton('Zero')
            self.buttons[f'Zero {self.num_to_axis[axis]}'].clicked.connect(lambda state, x=axis: self.zero_axis(x))
            self.layout.addWidget(self.buttons[f'Zero {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.labels[f'Position {self.num_to_axis[axis]}'] = QtW.QLabel(f'0.000000')
            self.layout.addWidget(self.labels[f'Position {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.labels[f'Unit {self.num_to_axis[axis]}'] = QtW.QLabel(f'{self.axis_display_label[axis]}')
            self.layout.addWidget(self.labels[f'Unit {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.buttons[f'Stop {self.num_to_axis[axis]}'] = QtW.QPushButton('Stop')
            self.buttons[f'Stop {self.num_to_axis[axis]}'].clicked.connect(lambda state, x=axis: self.stop_axis(x))
            self.layout.addWidget(self.buttons[f'Stop {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.lineEdits[f'Absolute {self.num_to_axis[axis]}'] = QtW.QLineEdit('00.0000')
            self.lineEdits[f'Absolute {self.num_to_axis[axis]}'].setInputMask('99.9999')
            self.layout.addWidget(self.lineEdits[f'Absolute {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.buttons[f'Move {self.num_to_axis[axis]}'] = QtW.QPushButton('Move')
            self.buttons[f'Move {self.num_to_axis[axis]}'].clicked.connect(
                lambda state, x=axis: self.move_axis_absolute(x))
            self.layout.addWidget(self.buttons[f'Move {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.lineEdits[f'Increment {self.num_to_axis[axis]}'] = QtW.QLineEdit('00.0000')
            self.lineEdits[f'Increment {self.num_to_axis[axis]}'].setInputMask('99.9999')
            self.layout.addWidget(self.lineEdits[f'Increment {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.buttons[f'- {self.num_to_axis[axis]}'] = QtW.QPushButton('-')
            self.buttons[f'- {self.num_to_axis[axis]}'].clicked.connect(
                lambda state, x=axis, sign=-1: self.increment_axis(x, sign))
            self.layout.addWidget(self.buttons[f'- {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.buttons[f'+ {self.num_to_axis[axis]}'] = QtW.QPushButton('+')
            self.buttons[f'+ {self.num_to_axis[axis]}'].clicked.connect(lambda state, x=axis, sign=1: self.increment_axis(x, sign))
            self.layout.addWidget(self.buttons[f'+ {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)

        column_counter += 1

        for axis in self.axis_display_order:
            self.boxes[f'CL {self.num_to_axis[axis]}'] = QtW.QCheckBox('Closed loop')
            self.boxes[f'CL {self.num_to_axis[axis]}'].clicked.connect(
                lambda state, x=axis: self.set_feedback_mode(state, x))
            self.layout.addWidget(self.boxes[f'CL {self.num_to_axis[axis]}'],
                                  row_counter + self.axis_display_order.index(axis), column_counter)
        column_counter += 1
        self.layout.addWidget(QtW.QLabel("Routines"), 12, 0)
        self.layout.addWidget(QtW.QLabel("Frequency (s)"), 12, 3)
        
        self.layout.addWidget(QtW.QLabel("Recipe Directory"), 12, 5)
        self.layout.addWidget(QtW.QLabel("Recipe file name"), 12, 7)

        self.layout.addWidget(QtW.QLabel("Recording (motion triggered, file created on click)"), 12, 12, 1, 3)
        self.layout.addWidget(QtW.QLabel("File name"), 12, 10)

        self.buttons['Timed Approach'] = QtW.QPushButton("Timed Approach")
        self.layout.addWidget(self.buttons['Timed Approach'], 13, 0)
        self.buttons['Timed Approach'].clicked.connect(lambda state, sign=1: self.timed_approach(sign))

        self.buttons['Timed Retract'] = QtW.QPushButton("Timed Retraction")
        self.layout.addWidget(self.buttons['Timed Retract'], 13, 1)
        self.buttons['Timed Retract'].clicked.connect(lambda state, sign=-1: self.timed_approach(sign))

        self.buttons['Stop Loop'] = QtW.QPushButton("Stop Loop")
        self.layout.addWidget(self.buttons['Stop Loop'], 13, 2)
        self.buttons['Stop Loop'].clicked.connect(self.stop_loop)

        self.lineEdits['Loop Freq'] = QtW.QLineEdit("1.0")
        self.lineEdits['Loop Freq'].setInputMask('9.9')
        self.layout.addWidget(self.lineEdits['Loop Freq'], 13, 3)
        
        self.lineEdits['Recipe Directory'] = QtW.QLineEdit("C:/Users/GGG-EXFOLIATOR/Documents/GitHub/Exfoliator/Recipes/")
        self.layout.addWidget(self.lineEdits['Recipe Directory'], 13, 5, 1, 2)
        path1=self.lineEdits['Recipe Directory'].text()
        
        self.lineEdits['Recipe file name'] = QtW.QLineEdit("Cleave V9.txt")
        self.layout.addWidget(self.lineEdits['Recipe file name'], 13, 7, 1, 2)
        path2=self.lineEdits['Recipe file name'].text()
        
        recpath=path1+path2
        self.recmode=0
        self.xrec=0
        self.yrec=0
        self.zrec=0
        self.trec=0
        self.varlist=0
        def recipe_load():
            path1=self.lineEdits['Recipe Directory'].text()
            path2=self.lineEdits['Recipe file name'].text()
            recpath = path1+path2
            print('Loading %s'%recpath)
            self.fbkmode,self.movmode,self.xrec,self.yrec,self.zrec,self.Frec,self.Trec=np.loadtxt(recpath,dtype=str, delimiter=' ', skiprows=5,usecols=(0,1,2,3,4,5,6),unpack=True)
            print('Recipe Loaded!')
            print(self.fbkmode)
            self.varlist=[self.fbkmode,self.movmode,self.xrec,self.yrec,self.zrec,self.Frec,self.Trec]
            #print(self.varlist)
        
        self.buttons['Load Recipe'] = QtW.QPushButton("Load Recipe")
        self.buttons['Load Recipe'].clicked.connect(lambda: recipe_load())
        self.buttons["Load Recipe"].setEnabled(True)
        self.layout.addWidget(self.buttons["Load Recipe"], 12, 9, 1, 1)
        
            
        self.buttons['Execute Recipe'] = QtW.QPushButton("Execute Recipe")
        self.buttons['Execute Recipe'].clicked.connect(lambda: self.recipe_queue(self.varlist,self.coefflist))
        self.layout.addWidget(self.buttons["Execute Recipe"], 13, 9, 1, 1)
        
        def coeff_load():
            path="C:/Users/GGG-EXFOLIATOR/Documents/GitHub/Exfoliator/Coefficients.txt"
            print('Loading Coefficients')
            self.coefflist=np.loadtxt(path,dtype=float,delimiter=', ', skiprows=12,usecols=(1),unpack=True)
            print(self.coefflist)
            xvel=self.coefflist[4]
            yvel=self.coefflist[5]
            zvel=self.coefflist[6]
            self.queue_manager.queue(1, f'1VEL{xvel}')
            self.queue_manager.queue(2, f'2VEL{yvel}')
            self.queue_manager.queue(3, f'3VEL{zvel}')
        self.buttons['Reload Coeffs'] = QtW.QPushButton("Reload Coeffs")
        self.buttons['Reload Coeffs'].clicked.connect(lambda: coeff_load())
        self.layout.addWidget(self.buttons["Reload Coeffs"], 12, 11, 1, 1)

        self.lineEdits['File name'] = QtW.QLineEdit("R22_")
        self.layout.addWidget(self.lineEdits['File name'], 13, 10, 1, 2)

        self.boxes['Rec Position'] = QtW.QCheckBox("Position")
        self.layout.addWidget(self.boxes['Rec Position'], 13, 12)
        self.boxes['Rec Position'].setEnabled(False)
        self.boxes['Rec Position'].clicked.connect(lambda state, x='Position': self.start_recording(state, x))

        self.boxes['Rec Frames'] = QtW.QCheckBox("Frames")
        self.layout.addWidget(self.boxes['Rec Frames'], 13, 13)
        self.boxes['Rec Frames'].setEnabled(False)
        self.boxes['Rec Frames'].clicked.connect(lambda state, x='Frames': self.start_recording(state, x))

        self.boxes['Rec Temp'] = QtW.QCheckBox("Temp")
        self.layout.addWidget(self.boxes['Rec Temp'], 13, 14)
        self.boxes['Rec Temp'].setEnabled(False)
        self.boxes['Rec Temp'].clicked.connect(lambda state, x='Temp': self.start_recording(state, x))

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for b in self.buttons.values():
            b: QtW.QPushButton
            #b.setEnabled(False)

        ##test
        #self.buttons['Map'].(False)(True)
        #self.buttons['Map'].clicked.connect(self._launch_subwindow)

    def start_recording(self, state, x):
        if x == 'Frames':
            if state:
                self.recordings[x] = self.lineEdits['File name'].text() + f'_{x}'
                self.start_video_signal.emit(self.recordings[x])
            else:
                self.stop_video_signal.emit(True)
        else:
            if state:
                self.recordings[x] = self.lineEdits['File name'].text() + f'_{x}'
                self.logger.add_new_log(self.recordings[x])
                line = 'Time;'
                if x == 'Position':
                    counter = 0
                    for axis in self.axis_display_order:
                        line += f'Calc {self.num_to_axis[axis]} ({self.axis_display_unit[counter]});Encoder {self.num_to_axis[axis]} ({self.axis_display_unit[counter]});'
                        counter+=1
                if x == 'Temp':
                    for keys in self.logger.temps.keys():
                        line += f'{keys};'
                self.logger.save_annotation(self.recordings[x], line)

    def timed_approach(self, sign):
        if self.active_loop:
            self.stop_loop()
        else:
            pass
        delay = float(self.lineEdits['Loop Freq'].text())
        self.loop_sign = sign

        self.loop_timer = Timer_Thread()
        self.loop_timer.record = True

        self.loop_timer.timer = delay
        self.loop_timer.signal.connect(self.timed_single_step)
        self.loop_timer.start()

        self.active_loop = True

    # def timed_single_step(self):
    #     axis = 7
    #     increment = self.loop_sign * float(self.lineEdits[f'Increment {self.num_to_axis[axis]}'].text())
    #     self.queue_manager.queue(axis, f'7MVR{increment}')
    #     self.queue_manager.queue(axis, f'7POS?')

    def stop_loop(self):
        print('Stopping timed loop')
        self.loop_timer.record = False
        self.active_loop = False
        self.loop_timer.signal.disconnect(self.timed_single_step)

    # def start_temp_recording(self):
    # self.temp_fname = self.lineEdits['Temp Filename'].text()
    # self.logger.add_new_log(self.temp_fname)
    # line = 'Time;'
    # for keys in self.logger.temps.keys():
    # line += f'{keys};'
    # self.logger.save_annotation(self.temp_fname, line)

    # self.timer = Timer_Thread()
    # self.timer.signal.connect(self.record_temp)
    # self.timer.timer = float(self.lineEdits['Temp Timer'].text())
    # self.timer.record = True
    # self.timer.start()

    # def stop_temp_recording(self):
    # self.timer.record = False
    # self.timer.signal.disconnect(self.record_temp)

    # def record_temp(self):
    # line = f'({datetime.now()});'
    # for temps in self.logger.temps.values():
    # line += f'{temps};'
    # self.logger.save_annotation(self.temp_fname, line)

    def emergency_stop(self):
        self.queue_manager.pause = True
        for motor in self.motors.values():
            motor.send('0EST')
        self.queue_manager.clear_queue()

    def clear_errors(self):
        print('Clearing errors')
        for motor in self.motors.values():
            for axis in motor.axes.values():
                self.queue_manager.queue(axis.number, f'{axis.number}ERR?')

    def change_parameters(self):
        print('Functionality not written')

    def move_axis_absolute(self, axis):
        print('Functionality not written')

    def toggle_motors(self, status):
        ##Can simplify this with dictionary mapping True to 1
        if status:
            print('Toggling motors on')
            for motor in self.motors.values():
                for axis in motor.axes.values():
                    self.queue_manager.queue(axis.number, f'{axis.number}MOT1')
        else:
            print("Toggling motors off")
            for motor in self.motors.values():
                for axis in motor.axes.values():
                    self.queue_manager.queue(axis.number, f'{axis.number}MOT0')

    def home_axis(self, axis):
        print(axis)
        #self.queue_manager.queue(axis, f'{axis}MLN')
        self.queue_manager.queue(axis, f'{axis}VEL8')
        self.queue_manager.queue(axis, f'{axis}MVR-200')
        self.labels[f'Home Status {self.num_to_axis[axis]}'].setText("Yes")

    def increment_axis(self, axis, sign=1):
        increment = sign * float(self.lineEdits[f'Increment {self.num_to_axis[axis]}'].text())
        self.queue_manager.queue(axis, f'{axis}POS?')
        self.queue_manager.queue(axis, f'{axis}MVR{increment}')
        
        print(f'{axis}MVR{increment}')
        print('Moving!', increment)
    def zero_axis(self, axis):
        self.queue_manager.queue(axis, f'{axis}ZRO')
        #self.queue_manager.queue(axis, f'{axis}POS?')
       # if axis == 2:
        #    self.queue_manager.queue(axis, f'3ZRO')
         #   self.queue_manager.queue(3, f'3POS?')

    def update_position(self, response):
        axis = response[0]
        pos = response[1].split(',')
        self.logger.position_data(axis, pos[0], pos[1])
        print(pos[0])
        if axis == 8 or axis == 9:
            self.labels[f'Position {self.num_to_axis[axis]}'].setText(pos[0].replace('#', ''))
        else:
            self.labels[f'Position {self.num_to_axis[axis]}'].setText(pos[1])
    
        if self.boxes["Rec Position"].isChecked():
            line = f'({datetime.now()});'
            for axis in self.axis_display_order:
                line += f'{self.logger.calc_pos[axis]};{self.logger.enc_pos[axis]};'
            self.logger.save_annotation(self.recordings['Position'], line)

        if self.boxes["Rec Temp"].isChecked():
            line = f'({datetime.now()});'
            for temps in self.logger.temps.values():
                line += f'{temps};'
            self.logger.save_annotation(self.recordings['Temp'], line)
    
        return axis, pos[0], pos[1]
    def update_pos2(self,axis):
        pos=self.axis_to_motor[axis].sendquiet(f'{axis}POS?')
        # self.MW= MotionWindow('dummy')
        # self.MW.labels[f'Position {self.num_to_axis[axis]}'].setText(axpos[1:9])
        pos=pos[1:9]
        self.labels[f'Position {self.num_to_axis[axis]}'].setText(pos)
        if self.boxes["Rec Position"].isChecked():
            line = f'({datetime.now()});'
            for axis in self.axis_display_order:
                line += f'{self.logger.calc_pos[axis]};{self.logger.enc_pos[axis]};'
            self.logger.save_annotation(self.recordings['Position'], line)

        if self.boxes["Rec Temp"].isChecked():
            line = f'({datetime.now()});'
            for temps in self.logger.temps.values():
                line += f'{temps};'
            self.logger.save_annotation(self.recordings['Temp'], line)
    
        return axis, pos
    def isfloat(self,incr):
        try:
            float(incr)
            return 1
        except ValueError:
            return 0
    def poschecker(self,axis):
        axpos=self.axis_to_motor[axis].send(f'{axis}POS?')
        # self.MW= MotionWindow('dummy')
        # self.MW.labels[f'Position {self.num_to_axis[axis]}'].setText(axpos[1:9])
        axpos=float(axpos[1:9])
        return axpos
    def sleepfunc(self,waittime):
        print('Sleepfunc says sleeping for '+str(int(waittime))+' seconds')
        start=float(time.time())
        now=float(time.time())
        goal=start+float(waittime)
        diff=0
        printflag=0
        while now<goal:
            now=float(time.time())
            diff=int(goal-now)
            if abs(diff-printflag)>=5:
                print('Waiting '+str(diff)+' more seconds')
                print('Weight'+str(weight_thread.get_weight(self,saveflag=1)))
                printflag=diff
    def timechecker(self,axis,incr):
        axpos=self.poschecker(axis)
        axvel=self.axis_to_motor[axis].send(f'{axis}VEL?')
        axvel=float(axvel[1:9])
        if axis<3:
            maxcheck=min(200,axpos+incr)
            destination=max(maxcheck,0)
        else:
            maxcheck=min(100,axpos+incr)
            destination=max(maxcheck,0)
        sleeptime=1+abs(axpos-destination)/abs(axvel)
        #print('Sleeping for ',sleeptime)
        #print(axpos,destination,axvel,sleeptime)
        return sleeptime
    def formfloat(self,floater):
        float1=str(floater)
        float2=float1[:7]
        float3=float(float2)
        return float3
    def approachfunc(self,boundary,outflag=0):
        boundary=self.formfloat(boundary)
        #self.sleepytare()
        tarew=weight_thread.get_weight(self)
        self.sleepfunc(3)
        location=float(self.poschecker(3))
        if location<boundary:
            print('Moving to boundary '+str(boundary)+'mm')
            self.queue_manager.queue(3, '3VEL10')
            self.queue_manager.queue(3, f'3MVA{boundary}')
            distance=boundary-location
            sleep_thread.sleepfunc(self,self.timechecker(3,distance))
        appvel=self.coefflist[7]
        backoff=self.coefflist[8]
        self.queue_manager.queue(3, f'3VEL{appvel}')
        print('Moving carefully')
        self.queue_manager.queue(3, f'3MVR30')
        counter=0
        self.globalweight=float(weight_thread.get_weight(self)-tarew)
        while self.globalweight<0.1:
            print('Approaching ', counter, '  ', self.globalweight,'  ',self.poschecker(3))
            self.globalweight=float(weight_thread.get_weight(self,saveflag=1))
            counter=counter+1
        print(self.globalweight)
        self.queue_manager.queue(3, f'3STP')
        self.queue_manager.queue(3, '3VEL0.01')
        print('Contact!')
        self.queue_manager.queue(3, f'3MVR{backoff}')
        
        sleep_thread.sleepfunc(self,5)
        if outflag==1:
            loc=float(self.poschecker(3))
            if abs(boundary-loc)<5:
                return loc
            else:
                return boundary-1
    def myloop(self,setweight):
        stepint=self.coefflist[12]
        stepslope=self.coefflist[11]
        offset=self.coefflist[13]
        tolperc=self.coefflist[1]/100
        tolg=self.coefflist[2]
        tolerance=abs(tolperc*setweight)+tolg #the listed accuracy of the scale, plus 1g
        self.globalweight=float(weight_thread.get_weight(self,saveflag=1))
        diff=setweight-self.globalweight
        self.newweight=0
        diff2=0
        self.queue_manager.queue(3, f'3VEL0.1')
        cal=8 #g/micron
        while abs(diff)>tolerance:
            self.oldweight=self.globalweight
            step=str(diff/cal/1000)
            step=float(step[:7])
            cap=min(stepint+abs(diff/stepslope),0.1)
            step=min(cap,step)
            step=max(-1*cap,step)
            step=self.formfloat(step)
            self.queue_manager.queue(3, f'3MVR{step}')
            if abs(diff2)>0:
                sleep_thread.sleepfunc(self,self.timechecker(3,step)+2)
            else:
                sleep_thread.sleepfunc(self,self.timechecker(3,step)-0.8)
            self.newweight=float(weight_thread.get_weight(self,saveflag=1))
            if abs(int(self.newweight)-self.newweight)<0.1:
                cal=max(0.2,(self.newweight-self.oldweight)/(1000*step)+offset)
                print('Getting closer, current weight ',self.newweight,' target ',setweight,' cal ',cal)
                self.globalweight=self.newweight
                diff=setweight-self.newweight
                diff2=self.newweight-self.oldweight
            else:
                sign=self.newweight*2
                failcount=0
                while (self.newweight)**2<abs(self.newweight):
                    step=-1*sign*0.1
                    print('Recovering from weight fault '+str(failcount)+'/10')
                    self.queue_manager.queue(3, f'3MVR{step}')
                    sleep_thread.sleepfunc(self,self.timechecker(3,step)+2)
                    self.newweight=float(weight_thread.get_weight(self,saveflag=1))
                    failcount=failcount+1
                    if failcount>10:
                        self.set_temp(0,0)
                        print('Exiting, please solve my problems yourself.')
                        sys.exit()
                cal=8
                sleep_thread.sleepfunc(self,1)
    def calloop(self,boundary,coefflist):
        self.sleepytare()
        self.globalweight=float(weight_thread.get_weight(self))
        name=str(int(time.time()))
        location=float(self.poschecker(3))
        if location<boundary:
            print('Moving to boundary '+str(boundary)+'mm')
            self.queue_manager.queue(3, '3VEL10')
            self.queue_manager.queue(3, f'3MVA{boundary}')
            distance=boundary-location
            sleep_thread.sleepfunc(self,self.timechecker(3,distance))
        self.queue_manager.queue(3, '3VEL0.1')
        print('Moving carefully')
        self.queue_manager.queue(3, '3MVR20')
        counter=0
        while self.globalweight<0.1:
            print('Approaching ', counter, '  ', self.globalweight)
            self.globalweight=float(weight_thread.get_weight(self))
            counter=counter+1
        self.queue_manager.queue(3, f'3STP') 
        print('Contact!')
        sleep_thread.sleepfunc(self,5)
        self.queue_manager.queue(3, '3VEL0.01')
        self.queue_manager.queue(3,'MVR-0.02')
        self.sleepytare()
        print('Lost contact! Calibrating now.')
        startpos=float(self.poschecker(3))
        cap=2000
        counter=0
        weight=float(weight_thread.get_weight(self))
        while weight<1000 and counter<=cap:
            f=open(f"{name}.txt","a+")
            #if weight>1:
             #   sleep_thread.sleepfunc(self,3)
            weight=float(weight_thread.get_weight(self))
            location=1000*(float(self.poschecker(3))-startpos)
            print(counter, weight)
            if int(weight)>5000:
                f.close()
                break
            writestr=str(location)+" "+str(weight)+'\n'
            f.write(writestr)
            f.close()
            self.queue_manager.queue(3, '3MVR0.001')
            counter=counter+1
        sleep_thread.sleepfunc(self,5)
        print('Calibration Complete')
        
    def recipe_queue(self,varlist,coefflist):
        #varlist has form [n,x,y,z,t] where each are arrays
        j=0 #array position
        boundary=81 #mm, the position z moves to without checking force
        while j<np.size(varlist)/7:
            k=2 #variable check
            fbkmode=varlist[0][j] #for later implementation of force as afeedback
            movemode=varlist[1][j]
            setweight=varlist[5][j]
            settemp=float(varlist[6][j])
            self.set_temp(settemp,0)
            self.set_temp(settemp,0)
            platetemp=float(self.get_temp(0))
            while abs(platetemp-settemp)>10:
                 sleep_thread.sleepfunc(self,10)
                 print("Waiting on temperature, current "+str(platetemp)+", goal "+str(settemp))
                 platetemp=float(self.get_temp(0))
            wait=0
            if fbkmode=='Pos':
                while k<5:
                    axis=k-1 #accident of the way the recipe is set up
                    incr=varlist[k][j]
                    if self.isfloat(incr)==1:
                        incr=float(incr)
                        if abs(incr)>0:                        
                            self.queue_manager.queue(axis, f'{axis}MVR{incr}')
                            #self.queue_manager.queue(axis, f'{axis}POS?')
                            tsleep=self.timechecker(axis,incr)
                            if movemode=='SER':
                                print('Serial')
                                sleep_thread.sleepfunc(self,tsleep)
                            if movemode=='PAR':
                                print('Parallel')
                                wait=max(wait,tsleep)
                    elif self.isfloat(incr)==0:
                        if 'HOLD' in incr:
                            waittime=incr.strip('HOLD')
                            print('I have been commanded to hold for'+waittime)
                            sleep_thread.sleepfunc(self,waittime)
                        else:
                            self.queue_manager.queue(axis, f'{axis}{incr}')
                        # elif 'MLN' in incr:
                        #     newv=incr.strip('MLN')
                        #     time.sleep(abs(incr)/2+1)
                        # elif 'MLP' in incr:
                        #     newv=incr.strip('MLP')
                        #     time.sleep(abs(incr)/2+1)
                        #self.queue_manager.queue(axis,f'0WTM{waittime}')
                    #this will probably result in very jerky motions? is there a defined velocity?
                    k=k+1
            elif fbkmode=='For': #tries to meeet a set force (weight in grams) read in from file
                forcecomm=varlist[5][j]
                
                if 'HOLD' in forcecomm:
                    incr=varlist[4][j]
                    waittime=float(incr.strip('HOLD'))
                    setforce=float(forcecomm.strip('HOLD'))
                    boundary=self.approachfunc(boundary,outflag=1)-1
                    self.myloop(setforce)
                    now=time.time()
                    goal=now+waittime
                    print('Holding force for '+str(waittime)+' seconds')
                    printflag=0
                    tolperc=self.coefflist[1]/100
                    tolg=self.coefflist[2]
                    tolerance=abs(tolperc*setforce)+tolg
                    while now<goal:
                        self.globalweight=float(weight_thread.get_weight(self))
                        if abs(setforce-self.globalweight)>tolerance:
                            print("Achieving force to hold!")
                            self.myloop(setforce)
                        else:
                            diff=int(goal-now) 
                            if abs(diff-printflag)>=5:
                                print('The weight is within the '+str(tolerance)+'g tolerance, '+str(self.globalweight)+'g Actual, '+str(setforce)+'g Goal')
                                print('Holding '+str(diff)+' more seconds')
                                printflag=diff
                        now=time.time()
                elif self.isfloat(forcecomm)==1:
                    setforce=float(forcecomm)
                    boundary=self.approachfunc(boundary,outflag=1)-1
                    self.myloop(setforce)
                else:
                    print('Badly formatted force')
            elif fbkmode=='Cal':
                print('Calibrating')
                boundary=self.approachfunc(boundary,outflag=1)-.5
                self.calloop(boundary,self.coefflist)
            elif fbkmode=='Ret':
                print('Retracting')
                incr=-100
                self.queue_manager.queue(3, '3VEL0.001')
                self.queue_manager.queue(3, f'3MVR{incr}')
                failcount=0
                while failcount<=5: #needs to read the same weight X times in a row to stop retracting
                    currweight=float(weight_thread.get_weight(self,saveflag=1))
                    print(currweight,failcount)
                    #self.queue_manager.queue(3, f'3POS?')
                    sleep_thread.sleepfunc(self,5)
                    if abs(float(weight_thread.get_weight(self))-currweight)<1:
                        failcount=failcount+1
                    else:
                        failcount=0
                backoff=-20
                self.queue_manager.queue(3, f'3STP')
                self.queue_manager.queue(3, '3VEL5')
                self.queue_manager.queue(3, f'3MVR{backoff}')
                tsleep=self.timechecker(3,backoff)
                sleep_thread.sleepfunc(self,tsleep)
            elif fbkmode=='Re2':
                print('Retracting')
                incr=-100
                self.queue_manager.queue(3, '3VEL0.002')
                self.queue_manager.queue(3, f'3MVR{incr}')
                loopcount=0
                start=time.time()
                while loopcount<100000:
                    currweight=float(weight_thread.get_weight(self))
                    print(loopcount,currweight)
                    sleep_thread.sleepfunc(self,1)
                    loopcount=loopcount+1
                self.queue_manager.queue(3, f'3STP')
                
            else:
                print("I don't understand the feedback mode",fbkmode)
            sleep_thread.sleepfunc(self,wait) #0 for serial, max travel time for parallel
            j=j+1
    def stop_axis(self, axis):
        self.queue_manager.pause = True
        if axis == 2:
            self.axis_to_motor[axis].send(f'{axis}STP')
        else:
            self.axis_to_motor[axis].send(f'{axis}STP')
        self.queue_manager.clear_queue()

    def set_feedback_mode(self, state, axis):
        print(axis)
        if self.boxes[f'CL {self.num_to_axis[axis]}'].isChecked():
            if '110' in self.axis_to_motor[axis].axes[axis].version:
                self.queue_manager.queue(axis, f'{axis}FBK3')
                if axis == 2:
                    self.queue_manager.queue(axis, f'3FBK3')
            elif '200' in self.axis_to_motor[axis].axes[axis].version:
                self.queue_manager.queue(axis, f'{axis}FBK2')
            # print('Closed loop')
        else:
            self.queue_manager.queue(axis, f'{axis}FBK0')
            if axis == 2:
                self.queue_manager.queue(axis, f'3FBK0')

    def closeEvent(self, event):
        self.closeSignal.emit(True)
        event.accept()


class Timer_Thread(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.timer = 1
        self.record = False

    def run(self):
        while self.record:
            self.signal.emit(True)
            time.sleep(self.timer)


class Queue_Manager(QtCore.QObject):
    ###Add method to allow addressing of axes on different controllers at the same time for synchronized motion
    position_signal = QtCore.pyqtSignal(object)
    queue_signal = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.cmd_queue = []
        self.axis_queue = []
        self.cmd_history = []
        self.axis_history = []
        self.response_history = []
        self.pause = False
        self.cmd_thread = CMD_Thread('dummy')
        self.cmd_thread.response_signal.connect(self.receive_response)
    def queue(self, axis, cmd,t=0):
        flag=0
        self.cmd_queue.append(cmd)
        self.axis_queue.append(axis)
        now=time.localtime(time.time())
        month=now.tm_mon
        day=now.tm_mday
        year=now.tm_year
        hour=now.tm_hour
        minute=now.tm_min
        sec=now.tm_sec
        name=str(year)+'_'+str(month)+'_'+str(day)+' Exfoliator Log.txt'
        timewrite=str(hour)+":"+str(minute)+'.'+str(sec)+' '
        now2=time.mktime(time.strptime(str(day)+' '+str(month)+' '+str(year), "%d %m %Y"))
        if flag==1:
            f=open(name,'a+')
        if len(self.cmd_queue) >= 1:
            #print("The Queue is ",self.cmd_queue)
            #self.send_next_cmd()
            cmd=self.cmd_queue[0]
            self.motor = self.axis_to_motor[axis]
            self.motor.send(cmd)
            if flag==1:
                deltime=str(time.time()-now2)
                writestr=timewrite+str(deltime+' Command' + cmd +'\n')
                f.write(writestr)
                
            #time.sleep(5)
            del self.cmd_queue[0]
        else:
            pass
        if flag==1:
            f.close()
        #self.queue_signal.emit([self.cmd_queue, self.axis_queue])

    def send_next_cmd(self):
        if self.pause:
            print("Commands not allowed to be sent at this time")
        else:
            axis = self.axis_queue[0]
            cmd = self.cmd_queue[0]
            print("Executing", cmd)
            print("The Queue is ",self.cmd_queue)
            self.cmd_thread.motor = self.axis_to_motor[axis]
            self.cmd_thread.cmd = cmd
            self.cmd_thread.start()
            #self.pause=True
    def undo_queue(self):
        del self.cmd_queue[-1]
        del self.axis_queue[-1]
        self.queue_signal.emit([self.cmd_queue, self.axis_queue])

    def receive_response(self, response):
        self.cmd_history.append(self.cmd_queue[0])
        self.axis_history.append(self.axis_queue[0])
        self.response_history.append(response)
        self.pause = False
        if 'POS' in self.cmd_queue[0]:
            self.position_signal.emit([self.axis_queue[0], response])
        del self.cmd_queue[0]
        del self.axis_queue[0]
        if len(self.cmd_queue) == 0:
            print("Queue empty")
        else:
            self.send_next_cmd()

    def clear_queue(self):
        self.cmd_queue = []
        self.axis_queue = []
        self.queue_signal.emit([self.cmd_queue, self.axis_queue])
        self.pause = False


class CMD_Thread(QtCore.QThread):
    response_signal = QtCore.pyqtSignal(object)

    def __init__(self, motor):
        super().__init__()
        self.motor = motor
        self.axis = None
        self.waiting = False
        self.cmd = None
        self.response = None
        self.sleep = False
        self.timer = 1
        self.disable_signal = False
        self.increment = 0

    def run(self):
        self.response = self.motor.send(self.cmd)
        self.response_signal.emit(self.response)
        
class sleep_thread(QtCore.QThread):
    # def get_weight(self,saveflag=0):
    #     print('sleeperweight')
    #     #weight=IKA.get_weight()
    #     bytecount=0
    #     # while bytecount < 4:
    #     #     FutekPort.reset_input_buffer()
    #     #     bytecount=FutekPort.in_waiting
    #     bytecount=0
    #     if FutekPort.in_waiting > 0:
    #         serialString = FutekPort.readline()
    #         #print(serialString)
    #         serialString2=serialString.decode("Ascii") #weight in pounds
    #         #print(type(serialString2),serialString2)
    #         weightlbs=float(serialString2[0:7])
    #         lbstogram=-1*453.592 #compression is positive
    #         weight=round(weightlbs*lbstogram,1)
    #         print(weight)
    #         if saveflag==1:
    #             now=time.localtime(time.time())
    #             month=now.tm_mon
    #             day=now.tm_mday
    #             year=now.tm_year
    #             name=str(year)+'_'+str(month)+'_'+str(day)+' Force Log.txt'
    #             now2=time.mktime(time.strptime(str(day)+' '+str(month)+' '+str(year), "%d %m %Y"))
    #             deltime=str(time.time()-now2)
    #             f=open(name,'a+')
    #             weight2=str(round(float(weight),2))
    #             writestr=str(deltime+' '+weight2+'\n')
    #             f.write(writestr)
    #             f.close()
    #         if abs(float(weight))<10000:# and float(weight)>-3000:
    #             return weight
    #         else:
    #             print('Weight fault!',weight)
    #             #if float(weight)<=-3000:
    #                 #return -0.5
    #             if abs(float(weight))>=10000:
    #                 return 0.5
    def sleepfunc(self,waittime):
        print('Sleepfunc says sleeping for '+str(int(waittime))+' seconds')
        start=float(time.time())
        now=float(time.time())
        goal=start+float(waittime)
        diff=0
        printflag=0
        while now<goal:
            now=float(time.time())
            diff=int(goal-now)
            if abs(diff-printflag)>=5:
                print('Waiting '+str(diff)+' more seconds')
                print('Weight'+str(weight_thread.get_weight(self,saveflag=1)))
                printflag=diff
class weight_thread(QtCore.QThread):    
    def get_weight(self,saveflag=0):
        #print('weighter weight')
        #weight=IKA.get_weight()
        bytecount=0
        while bytecount < 4:
             FutekPort.reset_input_buffer()
             bytecount=FutekPort.in_waiting
        bytecount=0
        if 1:
            serialString = FutekPort.readline()
            #print(serialString)
            serialString2=serialString.decode("Ascii") #weight in pounds
            #print(type(serialString2),serialString2)
            weightlbs=float(serialString2[0:7])
            lbstogram=-1*453.592 #compression is positive
            weight=round(weightlbs*lbstogram,1)
            print(weight)
            if saveflag==1:
                now=time.localtime(time.time())
                month=now.tm_mon
                day=now.tm_mday
                year=now.tm_year
                name=str(year)+'_'+str(month)+'_'+str(day)+' Force Log.txt'
                now2=time.mktime(time.strptime(str(day)+' '+str(month)+' '+str(year), "%d %m %Y"))
                deltime=str(time.time()-now2)
                f=open(name,'a+')
                weight2=str(round(float(weight),2))
                writestr=str(deltime+' '+weight2+'\n')
                f.write(writestr)
                f.close()
            if abs(float(weight))<10000:# and float(weight)>-3000:
                return weight
            else:
                print('Weight fault!',weight)
                #if float(weight)<=-3000:
                    #return -0.5
                if abs(float(weight))>=10000:
                    return 0.5
from PyQt5 import QtCore, QtWidgets as QtW
import time
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import QSizePolicy


class MotionWindow(QtW.QWidget):
    start_video_signal = QtCore.pyqtSignal(object)
    save_frame_signal = QtCore.pyqtSignal(object)
    stop_video_signal = QtCore.pyqtSignal(object)

    def __init__(self, logger):
        super().__init__()
        self.queue_manager = Queue_Manager()
        self.queue_manager.position_signal.connect(self.update_position)

        self.motors = {}
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

        self.logger = logger
        self.recordings = {}

        self.active_loop = False

        self.GUI_Elements()

    def connect_motor(self, connection_msg):
        if connection_msg[0] == 'MMC1' or connection_msg[0] == 'MMC2':
            self.motors[connection_msg[0]] = connection_msg[1]
            for axis in self.motors[connection_msg[0]].axes.values():
                self.available_axes.append(axis.number)
                print(connection_msg[0], axis.number)
                self.axis_to_motor[axis.number] = connection_msg[1]
                self.buttons[f'Home {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'Zero {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'Stop {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'+ {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons[f'- {self.num_to_axis[axis.number]}'].setEnabled(True)
                self.buttons['Motor On'].setEnabled(True)
                self.buttons['Motor Off'].setEnabled(True)
                # Homing for these disabled for safety
                if axis.number == 2 or axis.number == 3 or axis.number == 7 or axis.number == 8 or axis.number == 9:
                    self.buttons[f'Home {self.num_to_axis[axis.number]}'].setEnabled(False)
                    self.buttons["Timed Approach"].setEnabled(True)
                    self.buttons['Timed Retract'].setEnabled(True)
                    self.buttons['Stop Loop'].setEnabled(True)
                if axis.number == 2 or axis.number == 7 or axis.number == 8 or axis.number == 9:
                    self.boxes[f'CL {self.num_to_axis[axis.number]}'].setEnabled(False)

            if 7 in self.available_axes and 10 in self.available_axes:
                self.boxes['Microscope -> Sample Z'].setEnabled(True)

            if 2 in self.available_axes and 3 in self.available_axes and 8 in self.available_axes:
                self.boxes['Sample X -> Gonio1'].setEnabled(True)

            if 4 in self.available_axes and 9 in self.available_axes:
                self.boxes['Sample Y -> Gonio2'].setEnabled(True)

            if not self.motor_connected:
                self.motor_connected = True
                self.buttons["Axes Parameters"].setEnabled(True)
                self.buttons["Clear Errors"].setEnabled(True)
                self.buttons["EST Stop"].setEnabled(True)
                self.buttons["Map"].setEnabled(True)
                self.buttons["Jog"].setEnabled(True)
                self.buttons["CMD Line"].setEnabled(True)
                self.buttons["Load Rec"].setEnabled(True)
                self.boxes['Rec Position'].setEnabled(True)
                self.boxes['Rec Frames'].setEnabled(True)
                self.boxes['Rec Temp'].setEnabled(True)

            self.queue_manager.motors = self.motors
            self.queue_manager.axis_to_motor = self.axis_to_motor

            self.init_motor_settings(self.motors[connection_msg[0]].axes.values())

    def init_motor_settings(self, axes):
        for axis in axes:
            self.queue_manager.queue(axis.number, f'{axis.number}ZRO')
            self.queue_manager.queue(axis.number, f'{axis.number}POS?')
            self.queue_manager.queue(axis.number, f'{axis.number}FBK0')
            self.queue_manager.queue(axis.number, f'{axis.number}MOT0')

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
        
        self.buttons['Load Rec'] = QtW.QPushButton("Load Recipe")
        self.buttons['Load Rec'].clicked.connect(self.get_recipe())
        self.layout.addWidget(self.buttons["Load Rec"], 13, 9, 1, 1)

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
            self.lineEdits[f'Absolute {self.num_to_axis[axis]}'] = QtW.QLineEdit('0.0000')
            self.lineEdits[f'Absolute {self.num_to_axis[axis]}'].setInputMask('9.9999')
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
            self.lineEdits[f'Increment {self.num_to_axis[axis]}'] = QtW.QLineEdit('0.0000')
            self.lineEdits[f'Increment {self.num_to_axis[axis]}'].setInputMask('9.9999')
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
            self.buttons[f'+ {self.num_to_axis[axis]}'].clicked.connect(
                lambda state, x=axis, sign=1: self.increment_axis(x, sign))
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

        self.boxes["Microscope -> Sample Z"] = QtW.QCheckBox("Follow Z")
        self.layout.addWidget(self.boxes["Microscope -> Sample Z"], 2, column_counter)

        self.boxes["Sample X -> Gonio1"] = QtW.QCheckBox("Follow Gonio1")
        self.layout.addWidget(self.boxes["Sample X -> Gonio1"], 3, column_counter)

        self.boxes["Sample Y -> Gonio2"] = QtW.QCheckBox("Follow Gonio2")
        self.layout.addWidget(self.boxes["Sample Y -> Gonio2"], 4, column_counter)

        self.layout.addWidget(QtW.QLabel("Routines"), 12, 0)
        self.layout.addWidget(QtW.QLabel("Frequency (s)"), 12, 3)

        self.layout.addWidget(QtW.QLabel("Recording (motion triggered, file created on click)"), 12, 12, 1, 3)
        self.layout.addWidget(QtW.QLabel("File name"), 12, 10)
        
        self.layout.addWidget(QtW.QLabel("Recipe Directory"), 12, 5)
        self.layout.addWidget(QtW.QLabel("Recipe file name"), 12, 7)
        self.layout.addWidget(QtW.QLabel("Load Recipe"), 12, 9)
        
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

        self.lineEdits['File name'] = QtW.QLineEdit("R22_")
        self.layout.addWidget(self.lineEdits['File name'], 13, 10, 1, 2)
        
        self.lineEdits['Recipe Directory'] = QtW.QLineEdit("D:")
        self.layout.addWidget(self.lineEdits['Recipe Directory'], 13, 5, 1, 2)
        
        self.lineEdits['Recipe file name'] = QtW.QLineEdit("Recipe")
        self.layout.addWidget(self.lineEdits['Recipe file name'], 13, 7, 1, 2)

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
            b.setEnabled(False)

        ##test
        #self.buttons['Map'].setEnabled(True)
        #self.buttons['Map'].clicked.connect(self._launch_subwindow)

    def get_recipe(self):
        wdir=self.lineEdits['Recipe Directory'].text()
        #n,xsteps,ysteps,zsteps,tsteps
        recipename=self.lineEdits['Recipe file name'].text()
        n,x,y,z,t=np.loadtxt("%s/%s"%(recipename),dtype=float, delimiter=' ', skiprows=5,usecols=(1,3,5,7,9),unpack=True) 
        #gives you step n (from 0), the 3D cartesian step size, and the wait time after the step
        # units are in mm and seconds
        
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

    def timed_single_step(self):
        axis = 7
        increment = self.loop_sign * float(self.lineEdits[f'Increment {self.num_to_axis[axis]}'].text())
        self.queue_manager.queue(axis, f'7MVR{increment}')
        self.queue_manager.queue(axis, f'7POS?')

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
        if axis == 2 or axis == 7 or axis == 8 or axis == 9:
            print('Homing is disabled for this axis')
        else:
            self.queue_manager.queue(axis, f'{axis}HOM')

        self.labels[f'Home Status {self.num_to_axis[axis]}'].setText("Yes")

    def increment_axis(self, axis, sign):
        increment = sign * float(self.lineEdits[f'Increment {self.num_to_axis[axis]}'].text())
        if axis == 2:
            self.queue_manager.queue(axis, f'{axis}MVR{increment};3MVR{increment}')
            self.queue_manager.queue(axis, f'{axis}POS?')
            self.queue_manager.queue(3, f'3POS?')
        elif axis == 10:
            increment = -1 * increment
            self.queue_manager.queue(axis, f'{axis}MVR{increment}')
            self.queue_manager.queue(axis, f'{axis}POS?')
        else:
            self.queue_manager.queue(axis, f'{axis}MVR{increment}')
            self.queue_manager.queue(axis, f'{axis}POS?')
            if axis == 7 and self.boxes['Microscope -> Sample Z'].isChecked():
                increment = -1 * sign * float(self.lineEdits[f'Increment {self.num_to_axis[10]}'].text())
                if np.abs(increment) <= 100E-3:
                    self.queue_manager.queue(10, f'10MVR{increment}')
                    self.queue_manager.queue(10, f'10POS?')
                else:
                    print("Microscope increment too large to follow (restrict to less than 100 um)")
            if axis == 8 and self.boxes['Sample X -> Gonio1'].isChecked():
                increment = sign * float(self.lineEdits[f'Increment {self.num_to_axis[2]}'].text())
                self.queue_manager.queue(2, f'2MVR{increment};3MVR{increment}')
                self.queue_manager.queue(2, f'2POS?')
                self.queue_manager.queue(3, f'3POS?')

            if axis == 9 and self.boxes['Sample Y -> Gonio2'].isChecked():
                increment = sign * float(self.lineEdits[f'Increment {self.num_to_axis[4]}'].text())
                self.queue_manager.queue(4, f'4MVR{increment}')
                self.queue_manager.queue(4, f'4POS?')

    def zero_axis(self, axis):
        self.queue_manager.queue(axis, f'{axis}ZRO')
        self.queue_manager.queue(axis, f'{axis}POS?')
        if axis == 2:
            self.queue_manager.queue(axis, f'3ZRO')
            self.queue_manager.queue(3, f'3POS?')

    def update_position(self, response):
        axis = response[0]
        pos = response[1].split(',')
        self.logger.position_data(axis, pos[0], pos[1])
        if axis == 3:
            pass
        elif axis == 8 or axis == 9:
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

    def stop_axis(self, axis):
        self.queue_manager.pause = True
        if axis == 2:
            self.axis_to_motor[axis].send(f'{axis}STP;3STP')
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

    def queue(self, axis, cmd):
        self.cmd_queue.append(cmd)
        self.axis_queue.append(axis)
        if len(self.cmd_queue) == 1:
            self.send_next_cmd()
        else:
            pass
        self.queue_signal.emit([self.cmd_queue, self.axis_queue])

    def send_next_cmd(self):
        if self.pause:
            print("Commands not allowed to be sent at this time")
        else:
            axis = self.axis_queue[0]
            cmd = self.cmd_queue[0]
            self.cmd_thread.motor = self.axis_to_motor[axis]
            self.cmd_thread.cmd = cmd
            self.cmd_thread.start()

    def undo_queue(self):
        del self.cmd_queue[-1]
        del self.axis_queue[-1]
        self.queue_signal.emit([self.cmd_queue, self.axis_queue])

    def receive_response(self, response):
        self.cmd_history.append(self.cmd_queue[0])
        self.axis_history.append(self.axis_queue[0])
        self.response_history.append(response)
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

from PyQt5 import QtCore, QtWidgets as QtW
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import QSizePolicy
import os

LOGS_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')


class Logger(QtCore.QObject):
    new_annotation = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.logs = {}
        self.files = {}
        self.temps = {}
        self.logs['General'] = []
        self.start_time = datetime.now()
        self.prefix = os.path.join(LOGS_PATH, f'{datetime.today().strftime("%Y-%m-%d")}')
        self.create_file('General')
        self.log_writer = log_writer()
        self.counter = 0

        self.num_to_axis = {1: 'Stamp theta', 2: 'Sample X', 3: 'Sample X', 4: 'Sample Y',
                            5: 'Stamp X', 6: 'Stamp Y', 7: 'Sample Z', 8: 'Gonio 1 (left-right)',
                            9: 'Gonio 2 (up-down)', 10: 'Microscope Z'}

        self.axis_display_order = [10, 2, 4, 7, 8, 9, 5, 6, 1]
        self.axis_display_label = {}
        self.axis_display_unit = ['(deg)' if num == 1 or num == 8 or num == 9 else '(mm)' for num in
                                  self.axis_display_order]

        self.calc_pos = {}
        self.enc_pos = {}
        #self.calc_pos_arr = {}
        #self.encoder_pos_arr = {}
        #for key in self.num_to_axis.keys():
        #    self.calc_pos[key] = np.array([])
        #    self.encoder_pos[key] = np.array([])

    def add_new_log(self, category: str):
        self.logs[category] = []
        self.create_file(category)

    def create_file(self, category):
        np.savetxt(f'{self.prefix} {category}.txt', self.logs[category], delimiter=';', fmt="%s")
        self.files[category] = f'{self.prefix} {category}.txt'

    def receive_annotation(self, category, annotation):
        self.logs[category].append(f'({datetime.now()}) {annotation}')
        self.save_annotation(category, f'({datetime.now()}) {annotation}')
        self.new_annotation.emit(f'({datetime.now()}) {annotation}')

    def save_annotation(self, category, text):
        self.log_writer.log_file = open(self.files[category], 'a')
        self.log_writer.line = text
        self.log_writer.start()

    def controller_data(self, temps):
        for values in temps.values():
            self.temps[values.name] = values.value

    def sensor_data(self, temps):
        for values in temps.values():
            self.temps[values.name] = values.value

    def position_data(self, axis, calc_pos, enc_pos):
        self.calc_pos[axis] = float(calc_pos.replace("#", ''))
        self.enc_pos[axis] = float(enc_pos)

    def save_file(self):
        self.log_file.close()
        self.log_file = open(self.file_name, 'a')

    def close_file(self):
        self.log_file.close()


class log_writer(QtCore.QThread):
    def __init__(self):
        super().__init__()
        self.line = None
        self.log_file = None

    def run(self):
        self.log_file.write(self.line + '\n')
        self.log_file.close()


class LogWidget(QtW.QWidget):
    def __init__(self, logger):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.logger = logger
        self.logger.new_annotation.connect(self.write_annotation)
        self.layout = QtW.QGridLayout(self)

        # Text view
        self.textViewer = QtW.QTextEdit()
        self.textViewer.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.textViewer.setReadOnly(True)

        # Annotation Input
        self.annotation = QtW.QLineEdit()
        self.annotation.returnPressed.connect(self.send_annotation)

        self.layout.addWidget(self.textViewer)
        self.layout.addWidget(self.annotation)
        self.load_annotations()

    def load_annotations(self):
        for text in self.logger.logs['General']:
            if text == '':
                pass
            else:
                self.textViewer.append(text)

    def send_annotation(self):
        text = self.annotation.text()
        if text:
            self.logger.receive_annotation('General', f'*{text}')
            self.annotation.clear()

    def write_annotation(self, text):
        self.textViewer.append(text)

    def store_temps(self, temps):
        self.temps = temps


if __name__ == "__main__":
    app = QtW.QApplication([])
    logger = Logger()
    l = LogWidget(logger)
    l.show()
    app.exec()

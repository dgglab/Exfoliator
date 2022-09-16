from PyQt5 import QtCore, QtWidgets as QtW
from camera.autoz_camera_class import Camera
from motion_controller.mmc110 import MMC110
from temperature_controller.serial_utils import get_com_ports
HARDCODED_MMC_COM_PORT = "COM3"


class DeviceManager(QtCore.QObject):
    deviceConnected = QtCore.pyqtSignal(object)
    deviceDisconnected = QtCore.pyqtSignal(object)
    connectIssue = QtCore.pyqtSignal(object)

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.devices = {}
        self.active_ports = {}
        
    def connect_device(self, dev_type, port_list):
        if dev_type == 'Camera':
            try:
                self.devices['Camera'] = Camera()
                self.devices['Camera'].check_connection()
                if self.devices['Camera'].connection:
                    self.deviceConnected.emit([dev_type, self.devices['Camera']])
                    self.logger.receive_annotation("General", "Camera connected")
            except:
                self.connectIssue.emit(f'There was an issue connecting device type {dev_type[0]}')
                self.logger.receive_annotation("General", f'There was an issue connecting to camera')
                import traceback
                traceback.print_exc()
                
        elif dev_type == 'MMC1' or dev_type == 'IKA':
            port = port_list.currentText()
            print(dev_type, port)
            if port in self.active_ports.values():
                print(f'This port is already being used')
            else:
                try:
                    self.devices[dev_type] = MMC110(port)
                    self.deviceConnected.emit([dev_type, self.devices[dev_type]])
                    self.active_ports[dev_type] = port
                    self.logger.receive_annotation("General", f"{dev_type} connected")
                except:
                    self.logger.receive_annotation("General", f"{dev_type} failed connection")
                    import traceback
                    traceback.print_exc()


    def disconnect_device(self, dev_type):
        self.devices[dev_type].close()
        self.deviceDisconnected.emit(dev_type)


class DeviceManagerWindow(QtW.QMainWindow):
    connectRequest = QtCore.pyqtSignal(object)
    disconnectRequest = QtCore.pyqtSignal(object)
    closeSignal = QtCore.pyqtSignal(object)

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.setWindowTitle("Device Manager")
        self.widget = QtW.QWidget()
        self.setCentralWidget(self.widget)
        self.buttons = {}
        self.status_labels = {}
        self.lists = {}
        self.GUI_Elements()
        self.device_manager = DeviceManager(logger)


    def show(self):
        super().show()
        self.logger.receive_annotation('General', 'Device window opened')

    def GUI_Elements(self):
        self.layout = QtW.QGridLayout(self)
        labels = ["Device Type", "Device List", "", ""]

        for i in range(0, len(labels)):
            self.layout.addWidget(QtW.QLabel(labels[i]), 0, i)

        device_labels = ["Camera", "MMC (1)", "IKA"]
        for i in range(0, len(device_labels)):
            self.layout.addWidget(QtW.QLabel(device_labels[i]), i + 1, 0)

        self.buttons['Camera'] = QtW.QPushButton("Connect")
        self.buttons['Camera'].clicked.connect(lambda state, dev_type = 'Camera', port = 'dummy' :  self.device_manager.connect_device(dev_type, port))
        
        self.layout.addWidget(self.buttons['Camera'], 1, 2)
        

        self.lists['MMC1'] = QtW.QComboBox()
        self.lists['IKA'] = QtW.QComboBox()
        
        available_ports = get_com_ports()
        for p in available_ports:
            self.lists['MMC1'].addItem(p)
            self.lists['IKA'].addItem(p)
        self.layout.addWidget(self.lists['MMC1'], 2, 1)
        self.layout.addWidget(self.lists['IKA'], 3, 1)

        self.buttons['MMC1 Conn'] = QtW.QPushButton("Connect")
        self.buttons['MMC1 Conn'].clicked.connect(lambda state, dev_type='MMC1', port_list = self.lists['MMC1']: self.device_manager.connect_device(dev_type, port_list))
        
        self.buttons['IKA Conn'] = QtW.QPushButton("Connect")
        self.buttons['IKA Conn'].clicked.connect(lambda state, dev_type='IKA', port_list = self.lists['IKA']:  self.device_manager.connect_device(dev_type, port_list))

        self.buttons['MMC1 DConn'] = QtW.QPushButton("Disconnect")
        self.buttons['MMC1 DConn'].clicked.connect(lambda state, dev_type = 'MMC1':  self.device_manager.disconnect_device(dev_type))
        
        self.buttons['IKA DConn'] = QtW.QPushButton("Disconnect")
        self.buttons['IKA DConn'].clicked.connect(lambda state, dev_type = 'IKA':  self.device_manager.disconnect_device(dev_type))


        self.layout.addWidget(self.buttons['MMC1 Conn'], 2, 2)
        self.layout.addWidget(self.buttons['IKA Conn'], 3, 2)

        self.layout.addWidget(self.buttons['MMC1 DConn'], 2, 3)
        self.layout.addWidget(self.buttons['IKA DConn'], 3, 3)
        self.centralWidget().setLayout(self.layout)


if __name__ == "__main__":
    class DummyLogger:
        def receive_annotation(self, *args):
            print(*args)


    app = QtW.QApplication([])
    dm = DeviceManagerWindow(DummyLogger())
    dm.show()
    app.exec()

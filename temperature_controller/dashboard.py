from typing import Dict, List
import logging

from PyQt5.QtWidgets import QWidget, QGridLayout, QAbstractItemView, QHeaderView, QTableView, QTextEdit, QVBoxLayout, \
    QPushButton, QApplication, QDialog

from temperature_controller.controller_table import TemperatureControllerTableModel, TemperatureControllerTable
from temperature_controller.controller_table import ControllerTableRow, TemperatureControllerTableView, \
    TemperatureControllerTableDelegate, \
    ControllerTableRowControlButtons, ConfigureRowsDialog
from temperature_controller.poller import PollResponse, ChannelPoller
from temperature_controller.ikaret_manager import global_ikaret_manager
from temperature_controller.ikaret import IKARET
from temperature_controller.log_widget import logger, log_editor
from temperature_controller.sensor_table import TemperatureSensorTable, SensorTableRow

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

ALLOWED_CHANNEL_NAMES = [f"p{x}" for x in range(6)]





class TemperatureDashboard(QWidget):
    """
    Dashboard for system temperature controllers and sensors.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
        
    def init_ui(self):
        sensors = [x for x in global_ikaret_manager.sensors if x.name.lower().startswith("bot-") or x.name.lower() in [
            'festival', 'of', 'vdw', 'stacking', 'aaa', 'bbb', 'ccc'
        ]]
        self.temperature_sensor_table = TemperatureSensorTable(sensors)

        controllers = global_ikaret_manager.controllers
        self.temperature_controller_table = TemperatureControllerTable(controllers)


        self.log_display = self.build_log_display()
        self.dashboard_buttons = self.build_dashboard_buttons()

        main_layout = QGridLayout(self)
        main_layout.addWidget(self.temperature_controller_table, 0, 0, 1, 3)
        main_layout.addWidget(self.temperature_sensor_table, 1, 0)
        main_layout.addWidget(self.log_display, 1, 1)
        main_layout.addWidget(self.dashboard_buttons, 1, 2)
        self.setLayout(main_layout)


    def configure_controllers(self):
        dialog = ConfigureRowsDialog(parent=self)
        logger.info("Configure")

    def hold_all_controllers(self):
        logger.info("Hold all")

    def switch_all_controllers_off(self):
        # TODO: call off on all the controllers.
        logger.info("Switching all off")
    def get_weight(self):
        IKARET.get_weight()
    def build_log_display(self) -> QWidget:
        log_display = QTextEdit()
        log_display.setReadOnly(True)
        log_editor.connect_editor(log_display)
        logger.addHandler(log_editor)
        logger.info("Startup")
        return log_display

    def printfunc(self,arg):
        print(arg)
    def build_dashboard_buttons(self) -> QWidget:
        #self.IKARET=IKARET()
        # self.ikaman=global_ikaret_manager
        # self.ports=self.ikaman.ikarets
        # print(self.ports)
        #self.get_weight()=IKARET.get_weight()
        buttons = QWidget(self)
        buttons_layout = QVBoxLayout(buttons)
        configure_button = QPushButton("Configure Rows")
        configure_button.setEnabled(False)
        configure_button.clicked.connect(self.configure_controllers)
        hold_all_button = QPushButton("Hold All")
        hold_all_button.setEnabled(False)
        hold_all_button.clicked.connect(self.hold_all_controllers)
        newbutton=QPushButton("Test New Button")
        newbutton.setEnabled(True)
        #newbutton.clicked.connect(self.get_weight())
        switch_off_all_button = QPushButton("Switch Off All")
        switch_off_all_button.setEnabled(False)
        switch_off_all_button.clicked.connect(self.switch_all_controllers_off)
        buttons.setLayout(buttons_layout)
        for b in [configure_button, hold_all_button, switch_off_all_button,newbutton]:
            buttons_layout.addWidget(b)
        return buttons


if __name__ == "__main__":
    qApp = QApplication([])
    t = TemperatureDashboard()
    t.setGeometry(100, 100, 1080, 720)
    t.show()
    t.setWindowTitle('Temp')
    qApp.exec()


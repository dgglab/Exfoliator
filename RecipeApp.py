import sys
from PyQt5.QtWidgets import QMenu, QAction
import constants

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QMenuBar

from PyQt5 import QtWidgets as QtW

from camera.autoz_device_manager import DeviceManagerWindow
from camera.autoz_camera_viewport import CameraWindow
from temperature_controller.dashboard import TemperatureDashboard

from camera.autoz_test_window import MotionWindow

from camera.autoz_logger import Logger, LogWidget
import temperature_controller.hotplate as hp

class RangerMainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(100, 100, 1080, 720)
        self.logger = Logger()
        #self.device_manager_window = DeviceManagerWindow(self.logger)
        #self.cw = CameraWindow(logger=self.logger)
        self._init_ui()

        # Status bar
        self.statusBar()

        # Menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        file_menu = QMenu("&File", self)
        tools_menu = QMenu("&Tools", self)
        for x in [file_menu, tools_menu]:
            menu_bar.addMenu(x)

        tools_toolbar = QtW.QToolBar("&Tools", self)
        self.addToolBar(Qt.TopToolBarArea, tools_toolbar)

        # Actions
        self.a_open_device_manager = QAction("Open &Device Manager...", self)
        self.a_open_camera_viewport = QAction("Open &Camera Viewport...", self)

        # File Actions
        self.a_open_system_preferences = QAction("&System Preferences", self)
        self.a_edit_user_profiles = QAction("&User Profiles", self)
        self.a_quit = QAction("&Quit", self)

        # Add actions to menus
        file_menu.addActions([
            self.a_open_system_preferences,
            self.a_edit_user_profiles,
        ])
        file_menu.addSeparator()
        file_menu.addAction(self.a_quit)

        tools_menu.addActions([
            self.a_open_device_manager,
            self.a_open_camera_viewport,
        ])

        # Add actions to toolbars
        tools_toolbar.addActions([
            self.a_open_device_manager,
            self.a_open_camera_viewport,
        ])

        self.a_quit.triggered.connect(sys.exit)
        self.a_open_device_manager.triggered.connect(self.open_dev_manager)
        self.a_open_camera_viewport.triggered.connect(self.open_camera_viewport)
        self.a_open_camera_viewport.setEnabled(False)

        self.logger.receive_annotation("General", "App Started")

    def open_dev_manager(self):
        self.device_manager_window.show()

    def open_camera_viewport(self):
        self.cw.show()

    def _init_ui(self):
        log_widget = LogWidget(self.logger)
        self.setCentralWidget(log_widget)

        self.motion_doc_widget = QDockWidget("MotionDashboard", self)
        self.motion_controller_widget = MotionWindow(self.logger)
        self.motion_doc_widget.setWidget(self.motion_controller_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.motion_doc_widget)

        self.temperature_doc_widget = QDockWidget("TemperatureDashboard", self)
        self.temperature_widget = TemperatureDashboard()
        self.temperature_doc_widget.setWidget(self.temperature_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.temperature_doc_widget)

        #self.device_manager_window.device_manager.deviceConnected.connect(self.motion_controller_widget.connect_motor)


class RangerApp(QApplication):
    def __init__(self, argv=None):
        if argv is None:
            argv = []
        super().__init__(argv)
        self.main_window = RangerMainWindow()
        self.main_window.setWindowTitle(constants.MAIN_TITLE)
        self.main_window.show()


if __name__ == "__main__":
    app = RangerApp([])
    app.exec()

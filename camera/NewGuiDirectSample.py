from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QImage, QPixmap
import cv2

from .tisgrabber import tisgrabber



def np2pixmap(img):
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    q_img = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pix = QPixmap.fromImage(q_img)
    return pix

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        # Since we only have one camera in the system we don't really need to select anything.
        self.camera = tisgrabber.TIS_CAM()
        self.camera.ShowDeviceSelectionDialog()

        self.camera.SetVideoFormat("RGB32 (320x240)")
        self.camera.SetFrameRate(12.0)

        self.is_recording = False
        self.control_loop_frequency_s = 13  # Times per-second to interact with the system
        self.cv_resolution = (306, 256)

        self.show_mask = True
        self.show_coverage = True

        self.init_gui()

    def init_gui(self):
        central_widget = qtw.QWidget(self)
        self.setCentralWidget(central_widget)

        layout = qtw.QHBoxLayout(central_widget)
        central_widget.setLayout(layout)

        # Add Camera Viewports these should take up the most available space.
        self.main_viewport = qtw.QLabel("A")
        self.plot_viewport = qtw.QLabel("B")
        layout.addWidget(self.main_viewport)
        layout.addWidget(self.plot_viewport)

        # Add Camera Selection dropdown
        # This is currently limited to TisGrabber cameras only.

        # Get a list of tis cameras
        # Add the list to dropdown
        # available_cameras = Camera.devices
        # camera_selector = qtw.QComboBox()
        # camera_selector.addItems(
        #     [camera for camera in available_cameras]
        # )
        # layout.addWidget(camera_selector)
        # camera_selector.currentIndexChanged.connect(self._select_camera)

        self.config_section = qtw.QWidget()
        layout.addWidget(self.config_section)

        layout2 = qtw.QVBoxLayout()
        self.config_section.setLayout(layout2)
        self.startButton = qtw.QPushButton("start")
        self.startButton.pressed.connect(self.button_push)
        self.started = False
        self.bridge = CallbackUserdata()
        self.camera = Camera(self.bridge)
        self.bridge.signals.newimage.connect(self.process_new_frame)
        layout2.addWidget(self.startButton)

        self.mask_toggle = qtw.QCheckBox("Show Mask")
        self.overlay_toggle = qtw.QCheckBox("Show Overlay")
        layout2.addWidget(self.mask_toggle)
        layout2.addWidget(self.overlay_toggle)

        self.fps_double = qtw.QSpinBox()
        self.fps_double.valueChanged.connect(self.fps_change)
        layout2.addWidget(self.fps_double)

    def fps_change(self):
        self.camera.set_framerate(self.fps_double.value())

    def button_push(self):
        if self.started:
            self.camera.stop()
            self.started = False
            self.startButton.setText("Start")
        else:
            self.camera.start()
            self.started = True
            self.startButton.setText("Stop")

    def process_new_frame(self, frame):
        height, width, depth = frame.shape
        x = width//2
        y = height//2
        if self.mask_toggle.isChecked():
            frame = cv2.rectangle(frame, (x,y), (x +100, y+100), (200, 0, 0), 2)
        if self.overlay_toggle.isChecked():
            frame = cv2.rectangle(frame, (x,y), (x -100, y-100), (0, 200, 0), 4)
        self.main_viewport.setPixmap(np2pixmap(frame))


def main():
    app = qtw.QApplication([])
    win = MainWindow()
    win.show()
    app.exec()

if __name__ == "__main__":
    main()

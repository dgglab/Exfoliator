import sys, time, os
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QErrorMessage, QApplication, QToolBar, QAction, QComboBox
from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

from pathlib import Path

class MainCameraViewport(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_path = os.path.join(str(Path.home()), 'Desktop')
        print(self.save_path)

        # Window-level information
        self.setWindowTitle("Camera View")
        self.setGeometry(100, 100, 1080, 720)
        self.setStyleSheet("background:lightgrey;")
        self.status = QStatusBar()
        self.status.setStyleSheet("background:white;")
        self.setStatusBar(self.status)

        # Camera Viewport
        self.viewfinder = QCameraViewfinder()
        self.setCentralWidget(self.viewfinder)

        # Toolbar Add Toolbar
        toolbar = QToolBar("Camera toolbar")
        toolbar.setStyleSheet("background:white;")
        self.addToolBar(toolbar)

        # Capture action
        capture_action = QAction("Capture Photo", self)
        capture_action.setStatusTip("Capture a photo")
        capture_action.setToolTip("Capture photo")
        capture_action.triggered.connect(self.capture_image)
        toolbar.addAction(capture_action)

        # Camera Selector
        camera_selector = QComboBox()
        camera_selector.setStatusTip("Select Camera")
        camera_selector.setToolTip("Select Camera")
        self.available_cameras = QCameraInfo.availableCameras()
        camera_selector.addItems(
            [camera.description() for camera in self.available_cameras]
        )
        camera_selector.currentIndexChanged.connect(self.select_camera)
        toolbar.addWidget(camera_selector)
        print("available cameras:", self.available_cameras)

        self.select_camera(0)

    def select_camera(self, index):
        self.current_camera_name = self.available_cameras[index].description()
        self.camera = QCamera(self.available_cameras[index])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        self.camera.start()


        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.capture = QCameraImageCapture(self.camera)
        self.capture.error.connect(lambda err_msg, error, msg: self.alert(msg))
        # TODO: can we add a flash alert?
        self.capture.imageCaptured.connect(lambda d, i: self.status.showMessage("Image captured"))

        print("Supported Pixel Formats")
        for x in self.camera.supportedViewfinderPixelFormats():
            print("\t", x)

        print("Supported Viewfinder Resolutions")
        for x in self.camera.supportedViewfinderResolutions():
            print("\t", x)

        print("Supported Viewfinder Settings")
        for x in self.camera.supportedViewfinderSettings():
            print("\t", "max framerate:", x.maximumFrameRate())
            print("\t", "min framerate:", x.minimumFrameRate())

        print("Supported Viewfinder Framerates")
        for x in self.camera.supportedViewfinderFrameRateRanges():
            print("\t", "framerate range:", f"({x.minimumFrameRate}-{x.maximumFrameRate})")


    def alert(self, msg):
        error = QErrorMessage(self)
        error.showMessage(msg)

    def capture_image(self):
        print("time to capture image")
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        path = os.path.join(self.save_path,
                                          "%s-%s.jpg" % (
                                              self.current_camera_name,
                                              timestamp
                                          ))
        print(f"Path is {path}")
        self.capture.capture(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainCameraViewport()
    window.show()
    app.exec()


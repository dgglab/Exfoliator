import time, os

from PyQt5 import QtWidgets as QtW
from PyQt5 import QtCore, QtGui
import cv2 as cv
import matplotlib.pyplot as plt

DEFAULT_FILENAME_TEXT = "File name"
SAVE_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')

class CameraWindow(QtW.QMainWindow):
    closeSignal = QtCore.pyqtSignal(object)

    def __init__(self, logger):
        super().__init__()
        self.setWindowTitle('Camera')
        self.logger = logger
        self.camera = None
        self.buttons = {}
        self.widget = QtW.QWidget(self)
        self.setCentralWidget(self.widget)

        self.logger.logs['Camera'] = []
        self.logger.create_file('Camera')
        self.GUI_Elements()

    def show(self) -> None:
        self.logger.receive_annotation('General', 'Camera window opened')
        super().show()

    def connect_camera(self, camera):
        self.camera = camera
        self.camera.frameGrabber.data_signal.connect(self.receiveFrame)
        self.camera.frameGrabber.ref_signal.connect(self.receiveRefFrame)
        self.camera.frameGrabber.raw_data.connect(self.storeFrame)
        self.buttons['Start'].clicked.connect(self.camera.start_camera)
        self.buttons['Stop'].clicked.connect(self.camera.stop_camera)
        self.settings.buttons['Draw ROI'].clicked.connect(self.camera.frameGrabber.draw_crosshairs)

    def GUI_Elements(self):
        self.layout = QtW.QGridLayout(self)

        self.buttons['Start'] = QtW.QPushButton("Start Video")
        self.layout.addWidget(self.buttons['Start'], 0, 0)

        self.buttons['Stop'] = QtW.QPushButton("Stop Video")
        self.layout.addWidget(self.buttons['Stop'], 0, 1)

        self.buttons['Save'] = QtW.QPushButton("Save Image")
        self.buttons['Save'].clicked.connect(self.saveCameraImage)
        self.layout.addWidget(self.buttons['Save'], 0, 4)

        self.buttons['Record'] = QtW.QPushButton("Start Recording")
        self.buttons['Record'].clicked.connect(self.start_recording)
        self.layout.addWidget(self.buttons['Record'], 0, 5)

        self.filenameLine = QtW.QLineEdit(DEFAULT_FILENAME_TEXT)
        self.filenameLine.setFixedSize(160, 20)
        self.layout.addWidget(self.filenameLine, 0, 3)

        self.buttons['Settings'] = QtW.QPushButton("Camera Settings")
        self.buttons['Settings'].clicked.connect(self.showCameraSettings)
        self.layout.addWidget(self.buttons['Settings'], 0, 2)

        self.cameraFrame = QtW.QLabel()
        self.cameraFrame.setFixedSize(800, 800)
        self.cameraFrame.setScaledContents(True)
        self.layout.addWidget(self.cameraFrame, 2, 0, 1, 6)

        self.initCameraSettings()
        self.settings.buttons['Average Frames'].clicked.connect(self.adjust_frame_buffer)
        self.widget.setLayout(self.layout)

    def initCameraSettings(self):
        self.settings = secondaryWindow('Camera Settings')
        self.settings.resize(600, 600)

        self.settings.buttons = {}
        self.settings.buttons['Draw ROI'] = QtW.QPushButton('Draw')
        self.settings.layout.addWidget(self.settings.buttons['Draw ROI'], 0, 4)

        self.settings.lineEdits = {}
        self.settings.lineEdits['Radius'] = QtW.QLineEdit('150')
        self.settings.layout.addWidget(self.settings.lineEdits['Radius'], 0, 0)

        self.settings.lineEdits['X Offset'] = QtW.QLineEdit('0')
        self.settings.layout.addWidget(self.settings.lineEdits['X Offset'], 0, 1)

        self.settings.lineEdits['Y Offset'] = QtW.QLineEdit('0')
        self.settings.layout.addWidget(self.settings.lineEdits['Y Offset'], 0, 2)

        self.settings.buttons['Adjust ROI'] = QtW.QPushButton("Adjust")
        self.settings.layout.addWidget(self.settings.buttons['Adjust ROI'], 0, 3)
        self.settings.buttons['Adjust ROI'].clicked.connect(self.adjustCameraROI)

        self.settings.layout.addWidget(QtW.QLabel("Buffer Size"), 1, 0)
        self.settings.lineEdits['Buffer Size'] = QtW.QLineEdit('4')
        self.settings.layout.addWidget(self.settings.lineEdits['Buffer Size'], 1,1,1,2)

        self.settings.buttons['Average Frames'] = QtW.QPushButton('Average Frames')
        self.settings.layout.addWidget(self.settings.buttons['Average Frames'], 1, 3,1,2)

        #self.settings.frame = QtW.QLabel()
        #self.settings.frame.setFixedSize(400, 400)
        #self.settings.frame.setScaledContents(True)
        #self.settings.layout.addWidget(self.settings.frame, 1, 0, 1, 5)

    def showCameraSettings(self):
        self.settings.show()

    def adjustCameraROI(self):
        self.camera.frameGrabber.change_roi(int(self.settings.lineEdits['X Offset'].text()),
                                            -1 * int(self.settings.lineEdits['Y Offset'].text()), \
                                            int(self.settings.lineEdits['Radius'].text()))

    def saveCameraImage(self):
        name = self.filenameLine.text()
        if name == DEFAULT_FILENAME_TEXT:
            name = str(time.time())
        path = os.path.join(SAVE_PATH, f"{name}.png")
        plt.imsave(path, self.cameraImage)
        self.logger.receive_annotation('General', f'Frame saved as {path}.png')
        
    def create_video_writer(self, filename):
        if filename == DEFAULT_FILENAME_TEXT:
            filename = str(time.time())
        path = os.path.join(SAVE_PATH, f"{filename}.mkv")
        self.videoWriter = videoWriter(self.refImage,path)
        self.logger.receive_annotation('General', f'Video recording at {path}')

    def start_recording(self):
        if self.buttons['Record'].text() == 'Start Recording':
            filename = self.filenameLine.text()
            self.create_video_writer(filename)
            self.camera.frameGrabber.ref_signal.connect(self.write_video)
            self.buttons['Record'].setText('Stop Recording')
        else:
            self.videoWriter.writeVideo = False
            self.camera.frameGrabber.ref_signal.disconnect(self.write_video)
            self.stop_recording()
            self.buttons['Record'].setText('Start Recording')

    def write_video(self, ref):
        self.videoWriter.writeVideo = True
        self.videoWriter.frame = cv.cvtColor(self.refImage, cv.COLOR_RGB2BGR)
        self.videoWriter.start()
        self.videoWriter.quit()

    def stop_recording(self):
        self.videoWriter.out.release()

    def storeFrame(self, frame):
        self.cameraImage = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    def receiveFrame(self, frame):
        cameraImage = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        data = QtGui.QImage(cameraImage.data, cameraImage.shape[1], cameraImage.shape[0], QtGui.QImage.Format_RGB888)
        self.cameraFrame.setPixmap(QtGui.QPixmap.fromImage(data))

    def receiveRefFrame(self, frame):
        self.refImage = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        data = QtGui.QImage(self.refImage.data, self.refImage.shape[1], self.refImage.shape[0],
                            QtGui.QImage.Format_RGB888)
        #self.settings.frame.setPixmap(QtGui.QPixmap.fromImage(data))

    def adjust_frame_buffer(self):
        self.camera.frameGrabber.frame_buffer_size = int(self.settings.lineEdits['Buffer Size'].text())
        self.camera.frameGrabber.reset_buffer = True

    def closeEvent(self, event):
        self.closeSignal.emit(True)
        event.accept()


class videoWriter(QtCore.QThread):
    def __init__(self, frame, filename):
        super().__init__()
        self.frame = frame
        self.filename = filename
        self.writeVideo = False
        fourcc = cv.VideoWriter_fourcc(*'DIVX')
        self.out = cv.VideoWriter(f'{self.filename}.mkv', fourcc, 6, (self.frame.shape[0], self.frame.shape[1]))

    def run(self):
        if self.writeVideo:
            self.out.write(self.frame)
            self.writeVideo = False


class secondaryWindow(QtW.QWidget):
    def __init__(self, name):
        super().__init__()
        self.setWindowTitle(f'{name}')
        self.layout = QtW.QGridLayout(self)
        self.workers = {}

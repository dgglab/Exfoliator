from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore

from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

import cv2
import numpy as np


from skimage.draw import ellipse

from collections import deque

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

def apply_layout_grid(grid, layout):
    for i, row in enumerate(grid):
        for j, widget in enumerate(grid[i]):
            layout.addWidget(widget, i, j)

def imread(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def apply_blur(frame, k, s):
    return cv2.GaussianBlur(frame, (k, k), s, borderType=cv2.BORDER_DEFAULT)

def add_overlay(frame, overlay):
    new_frame = np.copy(frame)
    new_frame[np.where(overlay > 0)] = overlay[np.where(overlay > 0)]
    return new_frame

def add_mask(frame, mask):
    return add_overlay(frame, mask)

def diff(frame, base, mask, thresh):
    d = cv2.absdiff(frame, base)
    d[np.where(mask == 0)] = 0
    d[:, :, 2] = (d[:, :, 0] + d[:, :, 1] + d[:, :, 2]) // 3
    d[np.where(d >= thresh)] = 255
    d[np.where(d < thresh)] = 0
    d[:, :, :2] = 0
    return d


class CVDetector(qtw.QMainWindow):
    def __init__(self):
        super(CVDetector, self).__init__()
        # Class Properties
        self.timer = QtCore.QTimer()
        self.sample_frequency_s = 12 # Sample 12 times per second
        self.history_length = 100  # Samples to keep.
        self.history = deque(maxlen=self.history_length)
        self.history_plot_headroom = 10 # Plot x samples of open space for aesthetics.

        # CV Algorithm Parameters
        self.k = 21
        self.s = 60
        self.show_mask = False
        # Coverage Threshold
        self.coverage_threshold = 9
        self.contact_threshold = 0.3  # consider contact when 0.3 of the mask is covered

        # Window properties
        self.setGeometry(100, 100, 1080, 720)
        self.setStyleSheet("background:lightgrey;")
        # ViewFinder
        self.camera_viewfinder = QCameraViewfinder()

        #====================================================================================================
        #                                       TOOL AND STATUSBAR
        #====================================================================================================
        # Stausbar
        self.status = qtw.QStatusBar()
        self.status.setStyleSheet("background:white;")
        self.setStatusBar(self.status)

        # Toolbar
        toolbar = qtw.QToolBar("Camera")
        toolbar.setStyleSheet("background:white;")
        self.addToolBar(toolbar)

        # Approach action
        approach_action = qtw.QAction("Approach", self)
        approach_action.setStatusTip("Begin Auto Approach")
        approach_action.setToolTip("Begin Auto Approach")
        approach_action.triggered.connect(self.start_approach)
        toolbar.addAction(approach_action)

        # Camera Selector
        camera_selector = qtw.QComboBox()
        camera_selector.setStatusTip("Select Camera")
        camera_selector.setToolTip("Select Camera")
        self.available_cameras = QCameraInfo.availableCameras()
        camera_selector.addItems(
            [camera.description() for camera in self.available_cameras]
        )
        camera_selector.currentIndexChanged.connect(self.select_camera)
        toolbar.addWidget(camera_selector)

        #====================================================================================================
        #                                       PARAMETER UI COMPONENTS
        #====================================================================================================
        # Coverage Threshold
        self.parameters_widget = qtw.QWidget(self)
        self.coverage_threshold_label = qtw.QLabel("Coverage Threshold")
        self.coverage_threshold_input = qtw.QSpinBox()
        self.coverage_threshold_input.setValue(self.coverage_threshold)
        self.coverage_threshold_input.valueChanged.connect(self.update_coverage_threshold)

        # Contact Threshold
        self.contact_threshold_label = qtw.QLabel("Contact Threshold")
        self.contact_threshold_input = qtw.QSpinBox()
        self.contact_threshold_input.setValue(self.contact_threshold)
        self.contact_threshold_input.valueChanged.connect(self.update_contact_threshold)

        # Smoothing
        self.blur_std_label = qtw.QLabel("Smoothing")
        self.blur_std_input = qtw.QSpinBox()
        self.blur_std_input.setValue(self.s)
        self.blur_std_input.valueChanged.connect(self.update_std)

        # Current amount of coverage
        self.coverage_label = qtw.QLabel("Current coverage")
        self.coverage_value = qtw.QLabel("")

        # Show Mask Checkbox
        self.show_mask_label = qtw.QLabel("Show Mask")
        self.show_mask_checkbox = qtw.QCheckBox()
        self.show_mask_checkbox.clicked.connect(self.toggle_mask)

        # Layout the parameter buttons in a grid.
        parameter_layout = qtw.QGridLayout()
        _lay = [
            (self.coverage_threshold_label, self.coverage_threshold_input),
            (self.contact_threshold_label, self.contact_threshold_input),
            (self.blur_std_label, self.blur_std_input),
            (self.coverage_label, self.coverage_value),
            (self.show_mask_label, self.show_mask_checkbox)
        ]
        apply_layout_grid(_lay, parameter_layout)
        self.parameters_widget.setLayout(parameter_layout)

        #====================================================================================================
        #                                     CV PLAYER UI COMPONENTS
        #====================================================================================================
        # CV Frames components
        self.visuals_widget = qtw.QWidget()
        visuals_layout = qtw.QGridLayout()

        self.current_frame_label = qtw.QLabel()
        self.current_blurred_label = qtw.QLabel()
        self.current_contact_overlay_label = qtw.QLabel()
        self.plot_label = qtw.QLabel()
        _lay = [
            (self.current_frame_label, self.current_blurred_label),
            (self.current_contact_overlay_label, self.plot_label)
        ]
        apply_layout_grid(_lay, visuals_layout)
        self.visuals_widget.setLayout(visuals_layout)

        overall_layout = qtw.QGridLayout()
        overall_layout.addWidget(self.camera_viewfinder, 0, 0, 2, 4)
        overall_layout.addWidget(self.visuals_widget, 2, 0, 2, 3)
        overall_layout.addWidget(self.parameters_widget, 2, 0, 1, 4)
        widget = qtw.QWidget(self)
        widget.setLayout(overall_layout)
        self.setCentralWidget(widget)

    def update_coverage_threshold(self, value):
        self.coverage_threshold = value

    def update_contact_threshold(self, value):
        self.contact_threshold = value

    def select_camera(self, index):
        camera_selection = self.available_cameras[index]
        self.current_camera_name = camera_selection.description()
        self.camera = QCamera(camera_selection)
        self.camera.setViewfinder(self.camera_viewfinder)
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        self.camera.start()

        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.current_frame_capture = QCameraImageCapture(self.camera)
        self.current_frame_capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)
        self.current_frame_capture.error.connect(lambda err_msg, err, msg: self.alert(msg))

    def alert(self, msg):
        error = qtw.QErrorMessage(self)
        error.showMessage(msg)

    def capture_frame(self):
        self.current_frame_capture.capture()
        self.camera.
        # Get image from buffer

        return self.current_frame_capture.capture()

    def start_approach(self):
        self.base_frame = self.capture_frame()
        self.base_frame_shape = self.base_frame.shape
        h, w, d = self.base_frame.shape
        self.mask = np.zeros((h, w, 3), dtype=np.uint8)
        rr, cc = ellipse(h // 2, w // 2, h // 2.2, w // 2.2)
        self.mask[rr, cc, 0] = 255

        # while True:
        #     # Step
        #     pass
        #     # Decision
        #     if coverage > self.coverage_threshold:
        #         break


    def toggle_mask(self):
        self.show_mask = not self.show_mask
        self.draw_images()

    def update_threshold(self, value):
        self.coverage_threshold = value
        print(self.coverage_threshold)
        self.draw_images()

    def update_std(self, value):
        self.s = value
        print(self.s)
        self.draw_images()

    def reset(self):
        self.idx = 0
        self.history = deque(maxlen=self.history_length)

    def set_fps(self, fps):
        self.fps = fps

    def jump(self, idx):
        self.idx = idx
        return self.frames[self.idx]

    def play_forward(self):
        self.timer.timeout.connect(self.step_forward)
        self.timer.start(1000 // self.fps)

    def play_backwards(self):
        return self.play(backward=True)

    def pause(self):
        self.timer.stop()

    def step_backward(self):
        self.idx -= 1
        self.idx = max(self.idx, 0)
        self._do_step()

    def step_forward(self):
        if self.idx == self.len - 1:
            self.pause()
        else:
            self.idx += 1
            self._do_step()

    def draw_images(self):
        path = self.frames[self.idx]
        font = cv2.FONT_HERSHEY_SIMPLEX
        img = imread(path)

        blurred_img = apply_blur(img, self.k, self.s)
        diff_img = diff(blurred_img, apply_blur(self.base_frame, self.k, self.s), self.mask, self.coverage_threshold)
        overlay_img = add_overlay(img, diff_img)

        height, width, channel = img.shape
        # InputOutputArray img, const String &text, Point org, int fontFace, double fontScale, Scalar color,
        # int thickness=1, int lineType=LINE_8, bool bottomLeftOrigin=false
        # cv2.putText(img, f'x-{self.idx}', (0, height//2), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
        if self.show_mask:
            img = add_overlay(img, self.mask)
        self.current_frame_label.setPixmap(topixmap(img))
        self.current_blurred_label.setPixmap(topixmap(blurred_img))
        self.current_contact_overlay_label.setPixmap(topixmap(overlay_img))
        return diff_img

    def _do_step(self):
        diff_img = self.draw_images()
        coverage = self.calculate_coverage(diff_img)
        self.history.append(coverage)
        self.coverage_value.setText(f"{coverage:.3f}")
        self.draw_plot(coverage)

    def draw_plot(self, coverage):
        fig = Figure((self.base_frame_shape[1] / 100, self.base_frame_shape[0] / 100))
        canvas = FigureCanvas(fig)
        ax = fig.gca()
        values = [x * 100 for x in self.history]
        ax.plot(
            range(len(values)),
            values,
            'b-',
            linewidth=2
        )
        ax.set_xlim(0, len(values) + self.history_plot_headroom)
        ax.set_ylim(-1, 100)
        # ax.set_xlabel('Frame Index', fontsize=13)
        # ax.set_ylabel('Percentage Covered', fontsize=13)
        # ax.axvline(x=self.idx, color="r")

        ax.plot(len(values), self.history[-1] * 100, "rs")
        ax.annotate(f"{coverage * 100:.1f}%", (len(values) + 1, self.history[-1] * 100), color='r')
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        canvas.draw()
        width, height = fig.get_size_inches() * fig.get_dpi()
        width = int(width)
        height = int(height)
        plot = np.frombuffer(canvas.tostring_rgb(), dtype='uint8').reshape(height, width, 3)
        self.plot_label.setPixmap(topixmap(plot))

    def calculate_coverage(self, diff):
        bitmask = self.mask[:, :, 0] // 255
        total_area = np.sum(bitmask)
        covered_area = np.sum(diff[:, :, 2]//255)
        percent_covered = covered_area / total_area
        return percent_covered


def topixmap(img):
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    q_img = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pix = QPixmap.fromImage(q_img)
    return pix


if __name__ == "__main__":
    app = qtw.QApplication([])
    win = CVDetector()
    win.show()
    app.exec()
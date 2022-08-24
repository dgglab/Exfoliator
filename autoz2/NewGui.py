import time
import traceback
from collections import deque
from typing import List

import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import cv2
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from motion_controller.mmc110 import MMC110

from autoz2.Motor import Motor, EmulatedMotor
from autoz2.algorithm import Algorithm
from autoz2.approach import Approach, Sample, EventSample, EventTypes
from autoz2.utils import apply_layout_grid, np2pixmap, add_bitmask_overlay, trace
from autoz_camera_class import get_camera_class, CallbackUserdata, ReplayCamera, Camera

# Camera = get_camera_class()

APPROACH_NOT_STARTED = "Approach: Not Running"
APPROACH_STARTED = "Approach: Running"
EMULATED_MOTOR_KEY = "emulated"
MSG_CAM_NOT_CONNECTED = "Camera Not Connected"

HARD_CODED_MMC_AXIS = ("COM3", 7)


class MainWindow(qtw.QMainWindow):
    onStart = qtc.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.algorithm = Algorithm()
        self.camera_viewport_resolution = (740, 740)
        w, h = self.camera_viewport_resolution
        self.w = w
        self.h = h

        self.cv_display_resolution = (w//2, h//2)
        self.plot_viewport_resolution = (w, h//2)

        self.bridge = CallbackUserdata()
        self.camera = Camera(self.bridge)
        # self.camera = ReplayCamera(self.bridge, "./sample_videos/R22_017_Graphene_Approach2.mkv")
        self.bridge.signals.newimage.connect(self.handle_new_frame)
        self.camera_running = False

        self.approach = None
        self.mmc = MMC110(HARD_CODED_MMC_AXIS[0])
        self.motor = Motor(self.mmc, HARD_CODED_MMC_AXIS[1])
        # self.motor = EmulatedMotor(None, 0)

        self.fps_estimate=0
        self.last_fps_check = time.time()
        self.frames_since_last_fps_check = 0
        self.fps_estimate_timer = QTimer()
        self.fps_estimate_timer.timeout.connect(self._estimate_fps)
        self.fps_estimate_timer.start(500)

        self.frame = np.zeros(shape=(h, w, 3), dtype=np.uint8)

        self.init_gui()

        # Add an event to the event queue to be immediately processed when the app comes online.
        # Without going through this event signal, Python will attempt to evaluate the function prior to the hand-off
        # to the Qt event loop, which can cause issues if the function in question depends on Qt in some way.
        self.onStart.connect(self._on_start)
        self.onStart.emit()


    @trace
    def init_gui(self):
        central_widget = qtw.QWidget(self)
        self.setCentralWidget(central_widget)
        # Make a display comprised of a few sections
        # first, we have the primary viewport. To the right of this is a plot and the CV views.
        # Below both of these is the section for parameters
        # Start with a grid view
        top_level_layout = qtw.QGridLayout()
        central_widget.setLayout(top_level_layout)

        self.main_viewport = qtw.QLabel()
        start_frame = np.zeros(shape=(self.h, self.w, 3), dtype=np.uint8)
        start_frame = cv2.putText(start_frame, MSG_CAM_NOT_CONNECTED,
                                  (0, self.h//2),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_8, bottomLeftOrigin=False)
        self.main_viewport.setPixmap(np2pixmap(start_frame))
        self.main_viewport.setMaximumSize(self.w, self.h)
        top_level_layout.addWidget(self.main_viewport, 0, 0, 1, 1)

        # ----------------------------------------------------------------------------------------------------
        #                                            CV Frame
        # ----------------------------------------------------------------------------------------------------
        # The section on CV parts
        self.cv_frame = qtw.QFrame()
        cv_frame_layout = qtw.QGridLayout()
        self.cv_frame.setLayout(cv_frame_layout)

        # Start with a Label describing status
        self.approach_running_label = qtw.QLabel()
        self.approach_running_label.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
        self.approach_running_label.setFont(QFont("Helvetica", 16, 2))
        self.approach_running_label.setText(APPROACH_NOT_STARTED)
        cv_frame_layout.addWidget(self.approach_running_label, 0, 0)

        # the top row is going to be the 3 cv parts
        # the bottom row is the plot section, which spans 3 columns
        self.blurred_base_frame_label = qtw.QLabel()
        self.blurred_current_frame_label = qtw.QLabel()
        self.diff_frame_label = qtw.QLabel()
        # For all 3 frames they have the same resolution, whihc is the cv resolution
        # start_cv_frame = np.zeros(shape=(*self.cv_resolution[::-1], 3), dtype=np.uint8)
        start_cv_pixmap = np2pixmap(cv2.resize(self.frame, self.cv_display_resolution))
        self.blurred_base_frame_label.setPixmap(start_cv_pixmap)
        self.blurred_current_frame_label.setPixmap(start_cv_pixmap)
        self.diff_frame_label.setPixmap(start_cv_pixmap)
        # Now add these the to the to row of our layout
        for i, w in enumerate([self.blurred_base_frame_label, self.blurred_current_frame_label]):
            cv_frame_layout.addWidget(w, 1, i)

        # Now create the plot widget, which takes up the bottom 3 columns of the CV layout
        self.plot_viewport_label = qtw.QLabel("Plot")
        plot_first_frame = np.zeros(shape=(*self.plot_viewport_resolution[::-1], 3), dtype=np.uint8)
        self.plot_viewport_label.setPixmap(np2pixmap(plot_first_frame))
        cv_frame_layout.addWidget(self.plot_viewport_label, 2, 0, 1, 3)

        # Now add the CV piece to the top-level layout, where we occupy the 2nd column of the top row
        top_level_layout.addWidget(self.cv_frame, 0, 1, 2, 1)

        # ----------------------------------------------------------------------------------------------------
        #                                            Controls Frame
        # ----------------------------------------------------------------------------------------------------
        # Now we move onto the bottom row of the layout, which contains the parameters and controls for the app
        self.controls_frame = qtw.QFrame()
        controls_frame_layout = qtw.QGridLayout()
        self.controls_frame.setLayout(controls_frame_layout)
        top_level_layout.addWidget(self.controls_frame, 1, 0, 1, 1)

        # ALGO SECTIONS
        self.toggle_camera_feed_button = qtw.QPushButton("Start Camera")
        self.toggle_camera_feed_button.pressed.connect(self.toggle_camera_feed)
        self.camera_running = False

        # Start Experiment / Approach
        self.toggle_approach_button = qtw.QPushButton("Start Approach")
        self.toggle_approach_button.pressed.connect(self.toggle_approach)

        self.show_mask_checkbox = qtw.QCheckBox("Show Mask Outline")
        self.show_overlay_checkbox = qtw.QCheckBox("Show Overlay")

        # self.fps_double = qtw.QSpinBox()
        # self.fps_double.setValue(self.default_fps)
        # self.fps_double.valueChanged.connect(self.fps_change)

        # New approach
        self.burst_step_button = qtw.QPushButton("Burst Step")
        self.burst_step_button.pressed.connect(self.run_burst_steps)

        # focus
        self.step_focus_backward_button = qtw.QPushButton("-")
        self.step_focus_forward_button = qtw.QPushButton("+")
        self.step_focus_forward_button.pressed.connect(self.step_focus_forward)
        self.step_focus_backward_button.pressed.connect(self.step_focus_backward)
        self.step_focus_spinbox_label = qtw.QLabel("Focus Step Size")
        self.step_focus_spinbox = qtw.QDoubleSpinBox()
        self.step_focus_spinbox.setValue(0.000)
        self.step_focus_spinbox.setDecimals(4)

        # Motion And Step
        self.step_backward_button = qtw.QPushButton("-")
        self.step_forward_button = qtw.QPushButton("+")
        self.step_forward_button.pressed.connect(self.step_forward)
        self.step_backward_button.pressed.connect(self.step_backward)

        for w in [self.step_focus_forward_button, self.step_focus_backward_button, self.step_backward_button, self.step_forward_button]:
            w.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)

        self.step_size_spinbox_label = qtw.QLabel("Z Step Size")
        self.step_size_spinbox = qtw.QDoubleSpinBox()
        self.step_size_spinbox.setDecimals(4)
        self.step_size_spinbox.setValue(0.0001)
        self.step_size_spinbox.setMaximum(0.2)

        self.autoz_frequency_label = qtw.QLabel("AutoZ Step Frequency (HZ)")
        self.autoz_frequency_spinbox = qtw.QSpinBox()
        self.autoz_frequency_spinbox.setValue(10)
        self.autoz_frequency_spinbox.setMaximum(30)
        self.autoz_max_steps_label = qtw.QLabel("AutoZ Max Steps")
        self.autoz_max_steps_spinbox = qtw.QSpinBox()
        self.autoz_max_steps_spinbox.setMaximum(100)
        self.autoz_max_steps_spinbox.setValue(100)

        # Sliders
        # self.smoothing_strength_slider_label = qtw.QLabel("Smoothing\nStrength")
        # self.smoothing_strength_slider = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        # self.smoothing_strength_slider.setValue(self.algorithm.s)
        # self.smoothing_strength_slider.valueChanged.connect(self.smoothing_strength_changed)

        # self.difference_threshold_slider_label = qtw.QLabel("Image Difference\nThreshold")
        # self.difference_threshold_slider = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        # self.difference_threshold_slider.setValue(self.algorithm.difference_threshold)
        # self.difference_threshold_slider.valueChanged.connect(self.difference_threshold_changed)

        self.contact_decision_threshold_slider_label = qtw.QLabel("Contact Decision\nThreshold")
        self.contact_decision_threshold_slider = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        self.contact_decision_threshold_slider.setValue(self.algorithm.difference_threshold)
        self.contact_decision_threshold_slider.valueChanged.connect(self.contact_decision_threshold_changed)
        self.contact_decision_threshold_slider.setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Fixed)

        grid = [
            [self.step_focus_spinbox_label, self.step_focus_spinbox, self.step_focus_backward_button, self.step_focus_forward_button],
            [self.step_size_spinbox_label, self.step_size_spinbox, self.step_backward_button, self.step_forward_button],
            [self.autoz_frequency_label, self.autoz_frequency_spinbox],
            [self.autoz_max_steps_label, self.autoz_max_steps_spinbox],
            [self.toggle_camera_feed_button, self.toggle_approach_button],
            [self.contact_decision_threshold_slider, self.show_mask_checkbox, self.show_overlay_checkbox],
        ]
        apply_layout_grid(grid, controls_frame_layout)
        controls_frame_layout.addWidget(self.burst_step_button, 2, 2, 1, 2)

        self.n_burst_steps = 1000
        self.burst_step_counter = 0
        self.auto_step_timer = QTimer()
        self.auto_step_timer.timeout.connect(self.burst_step_forward)

    @trace
    def _step(self, amount):
        self.motor.step(amount)
        # self.camera.cur_video_frame_index +=1 # TODO: REMOVE
        # if self.approach and self.approach.running:
        #     self.cv_pipeline()
        #     self.draw_plot()

    def step_forward(self):
        self._step(float(self.step_size_spinbox.value()))

    def step_backward(self):
        self._step(-float(self.step_size_spinbox.value()))

    def _step_focus(self, amount):
        self.mmc.send(f"10MVR{amount}")

    def step_focus_forward(self):
        self._step_focus(-float(self.step_focus_spinbox.value()))

    def step_focus_backward(self):
        self._step_focus(float(self.step_focus_spinbox.value()))



    def burst_step_forward(self):
        if self.burst_step_counter < int(self.autoz_max_steps_spinbox.value()):
            self.step_forward()
            self.burst_step_counter += 1

    def run_burst_steps(self):
        if self.approach and not self.approach.contact_detected:
            self.burst_step_counter = 0
            self.auto_step_timer.start(1000//self.autoz_frequency_spinbox.value())

    def smoothing_strength_changed(self):
        self.algorithm.s = self.smoothing_strength_slider.value()

    def difference_threshold_changed(self):
        self.algorithm.difference_threshold = float(self.difference_threshold_slider.value())

    def contact_decision_threshold_changed(self):
        self.algorithm.contact_decision_threshold = self.contact_decision_threshold_slider.value()
        self.draw_plot()

    # def set_motor(self):
    #     value = self.motor_select_combobox.currentText()
    #     if value == EMULATED_MOTOR_KEY:
    #         self.motor = EmulatedMotor()
    #     else:
    #         self.motor = Motor()

    @trace
    def _on_start(self):
        self.toggle_camera_feed()
        # self.motor_select_dialog = qtw.QDialog(self)
        # layout = qtw.QVBoxLayout()
        # self.motor_select_combobox = qtw.QComboBox()
        # self.ok_btn = qtw.QPushButton("Confirm")
        # self.ok_btn.clicked.connect(self.motor_select_dialog.close)
        # self.motor_select_dialog.finished.connect(self.set_motor)
        # for i in range(5):
        #     self.motor_select_combobox.addItem(str(i))
        # layout.addWidget(self.motor_select_combobox)
        # layout.addWidget(self.ok_btn)
        #
        # self.motor_select_dialog.setLayout(layout)
        # self.motor_select_dialog.setModal(True)
        # self.motor_select_dialog.show()

    @trace
    def toggle_camera_feed(self):
        if self.camera_running:
            if self.approach and self.approach.running:
                self.toggle_approach()
            self.camera.stop()
            self.camera_running = False
            self.toggle_camera_feed_button.setText("Start Camera")
        else:
            self.camera.start()
            self.camera_running = True
            self.toggle_camera_feed_button.setText("Stop Camera")

    @trace
    def toggle_approach(self):
        if self.approach and self.approach.running:
            # Wrap up recording
            self.approach.stop()
            self.approach.save()
            self.toggle_approach_button.setText("Start Approach")
            self.approach_running_label.setText(APPROACH_NOT_STARTED)
            self.approach_running_label.setStyleSheet("background-color: none")
            self.cv_pipeline()
            self.draw_plot()
        else:
            if not self.camera_running:
                self.toggle_camera_feed()
            self.approach = Approach()
            self.step_forward()
            self.toggle_approach_button.setText("Stop Approach")
            self.approach_running_label.setText(APPROACH_STARTED)
            self.approach_running_label.setStyleSheet("background-color: yellow")


    def _estimate_fps(self):
        now = time.time()
        time_delta = now - self.last_fps_check
        self.fps_estimate = self.frames_since_last_fps_check / time_delta
        self.frames_since_last_fps_check = 0
        self.last_fps_check = now
        # TODO: cheat, fix this
        if self.approach and self.approach.running:
            self.cv_pipeline()
            self.draw_plot()

    def handle_new_frame(self, frame):
        self.frame = cv2.resize(frame, self.camera_viewport_resolution)
        self.frames_since_last_fps_check += 1
        self.redraw_camera_viewport()

    def redraw_camera_viewport(self):
        frame = np.copy(self.frame)
        if self.show_mask_checkbox.isChecked():
            frame = add_bitmask_overlay(frame, cv2.resize(self.algorithm.mask_outline, self.camera_viewport_resolution), color=(0, 255, 0))

        if self.show_overlay_checkbox.isChecked() and self.algorithm.overlapped is not None:
            frame = add_bitmask_overlay(frame, cv2.resize(self.algorithm.overlapped, self.camera_viewport_resolution))

        w, h = self.camera_viewport_resolution
        frame = cv2.putText(frame, f"fps:{self.fps_estimate: .2f}", (int(0.01*w), int(0.05 * h)), cv2.FONT_HERSHEY_SIMPLEX,fontScale=1, color=(255, 0, 0), thickness=3, bottomLeftOrigin=False)
        self.main_viewport.setPixmap(np2pixmap(frame))

    def cv_pipeline(self):
        coverage_estimation = float(self.algorithm.run(self.frame))
        now = time.time()
        self.approach.tracked[self.approach.TS_ALGO_KEY].append(Sample(coverage_estimation, now))
        if not self.approach.contact_detected and coverage_estimation >= self.algorithm.contact_decision_threshold:
            self.approach.contact_detected = True
            self.approach.tracked[self.approach.TS_EVENT_KEY].append(EventSample(EventTypes.CONTACT, now))
            self.auto_step_timer.stop()

        self.blurred_base_frame_label.setPixmap(np2pixmap(cv2.resize(self.algorithm.base_frame, self.cv_display_resolution)))
        if self.algorithm.thresholded is not None:
            thresholded_with_extra_dim = cv2.cvtColor(self.algorithm.thresholded, cv2.COLOR_GRAY2RGB)
            thresholded_with_extra_dim[thresholded_with_extra_dim > 0] = 255
            self.blurred_current_frame_label.setPixmap(np2pixmap(cv2.resize(thresholded_with_extra_dim, self.cv_display_resolution)))

    def draw_plot(self):
        # Create a figure with the desired resolution. Note that matplotlib does not deal in pixels directly, for some
        # reason. Instead, you need to convert from the desired pixels into inches, which requires knowledge of the
        # DPI parameter. The default is 100. The equation is px = inches * dpi => inches = px/dpi.
        # There was some page on the matplotlib documentation which discussed this,
        # but I can't find it. Refer to https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
        dpi = 100
        w, h = self.plot_viewport_resolution
        fig = Figure(figsize=(w/dpi, h/dpi), dpi=dpi)
        canvas = FigureCanvas(fig)
        ax = fig.gca()

        ymin, ymax = (0, 100)
        xmin, xmax = (-10, 0)

        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        # Plot values as second diffs from now
        now = time.time()
        if self.approach:
            _values: List[Sample] = self.approach.tracked[self.approach.TS_ALGO_KEY].values
            x_values = [x.timestamp-now for x in _values]
            y_values = [x.value for x in _values]
            ax.plot(
                x_values,
                y_values,
                'b-',
                linewidth=2
            )
            ax.plot(0, y_values[-1], "rs")

            # Plot Events
            for e in self.approach.tracked[self.approach.TS_EVENT_KEY].values:
                e: EventSample
                event_name = e.value
                event_time = e.timestamp
                offset_event_time = event_time - now
                ax.axvline(x=offset_event_time, color='b')
                ax.annotate(event_name, (offset_event_time, ymax-5), color='b')


        # Plot Threshold
        ax.axhline(y=self.algorithm.contact_decision_threshold, color="r")
        ax.annotate(f"contact threshold: {self.algorithm.contact_decision_threshold}", (xmin+1, self.algorithm.contact_decision_threshold + 1), color='r')

        canvas.draw()
        plot = np.frombuffer(canvas.tostring_rgb(), dtype='uint8').reshape(h, w, 3)
        self.plot_viewport_label.setPixmap(np2pixmap(plot))


if __name__ == "__main__":
    app = qtw.QApplication([])
    win = MainWindow()
    win.show()
    app.exec()

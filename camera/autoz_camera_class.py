from PyQt5 import QtCore
import ctypes
import os
import numpy as np
import cv2 as cv

local_dir = os.path.abspath(os.path.dirname(__file__))
ic = ctypes.cdll.LoadLibrary(os.path.join(local_dir, "tisgrabber/tisgrabber_x64.dll"))
from camera.tisgrabber import tisgrabber as tis


class WorkerSignal(QtCore.QObject):
    frame = QtCore.pyqtSignal(object)


class CameraData(ctypes.Structure):
    data_signal = WorkerSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None


class Camera():
    def __init__(self, device='Dummy Camera'):
        self.ic = ic
        tis.declareFunctions(self.ic)
        self.ic.IC_InitLibrary(0)
        self.hGrabber = self.ic.IC_CreateGrabber()
        self.connection = False
        self.connectDevice()

    def connectDevice(self):
        device_count = self.ic.IC_GetDeviceCount()
        device_name = tis.D(self.ic.IC_GetUniqueNamefromList(0))
        print("Unique Name : {}".format(tis.D(self.ic.IC_GetUniqueNamefromList(0))))
        self.ic.IC_OpenDevByUniqueName(self.hGrabber, tis.T(device_name))
        # self.ic.IC_printItemandElementNames(self.hGrabber)
        self.frameGrabber = cameraFrames(self.hGrabber)

    def check_connection(self):
        if self.ic.IC_IsDevValid(self.hGrabber):
            self.connection = True

    def start_camera(self):
        self.frameGrabber.start()

    def stop_camera(self):
        self.frameGrabber.cameraActive = False
        self.frameGrabber.stopDevice()
        self.frameGrabber.quit()

    def disconnect_device(self):
        self.ic.IC_ReleaseGrabber(self.hGrabber)


class cameraFrames(QtCore.QThread):
    data_signal = QtCore.pyqtSignal(object)
    ref_signal = QtCore.pyqtSignal(object)
    raw_data = QtCore.pyqtSignal(object)

    def __init__(self, hGrabber):
        super().__init__()
        self.ic = ic
        tis.declareFunctions(self.ic)
        self.ic.IC_InitLibrary(0)
        self.Px = 800
        self.Py = 800
        self.fps = 240
        self.hGrabber = hGrabber
        self.ic.IC_SetVideoFormat(self.hGrabber, tis.T(f"RGB32 ({self.Px}x{self.Py})"))
        self.ic.IC_SetFrameRate(self.hGrabber, ctypes.c_float(self.fps))
        self.cameraData = CameraData()
        self.cameraData.data_signal.frame.connect(self.frame_handler_two)

        self.cameraActive = False
        self.crosshairs = True
        self.calc_mask = True
        self.pause = False
        
        self.radius = 150
        self.x_offset = 0
        self.y_offset = 0
        
        self.frame_buffer = np.zeros((1,self.Px, self.Py, 3))
        self.buffer_count = 1
        self.frame_buffer_size = 4
        self.reset_buffer = False
        self.grabFrameCallbackfunc = self.ic.FRAMEREADYCALLBACK(self.grabFrameCallback)
        self.ic.IC_SetFrameReadyCallback(self.hGrabber, self.grabFrameCallbackfunc, self.cameraData)

    def run(self):
        self.mask = np.zeros((2 * self.radius, 2 * self.radius))
        for i in range(0, 2 * self.radius):
            for j in range(0, 2 * self.radius):
                if float((i - self.radius) ** 2 + (j - self.radius) ** 2) < self.radius ** 2:
                    self.mask[i][j] = 1
        self.calc_mask = False
        self.startDevice()

    def startDevice(self):
        if self.ic.IC_IsDevValid(self.hGrabber):
            self.cameraActive = True
            self.ic.IC_SetContinuousMode(self.hGrabber, 0)
            self.ic.IC_StartLive(self.hGrabber, 1)

    def stopDevice(self):
        self.cameraActive = False
        if self.ic.IC_IsDevValid(self.hGrabber):
            self.ic.IC_StopLive(self.hGrabber)

    def stop(self):
        self.cameraActive = False
        if self.ic.IC_IsDevValid(self.hGrabber):
            self.ic.IC_StopLive(self.hGrabber)
        self.radius = 150
        self.wait()

    def draw_crosshairs(self):
        if self.crosshairs:
            self.crosshairs = False
        else:
            self.crosshairs = True

    def get_radius(self):
        return self.text_radius

    def change_roi(self, x_offset, y_offset, radius):
        self.x_offset = x_offset
        self.y_offset = y_offset
        ##        if 2*radius > int(self.shape[1]):
        ##            self.text_radius = 150
        ##        else:
        ##            self.text_radius = radius
        if radius != self.radius:
            self.calc_mask = True
            self.radius = radius

    def frame_handler(self, frame):
        if self.calc_mask:
            self.mask = np.zeros((2 * self.radius, 2 * self.radius))
            for i in range(0, 2 * self.radius):
                for j in range(0, 2 * self.radius):
                    if float((i - self.radius) ** 2 + (j - self.radius) ** 2) < self.radius ** 2:
                        self.mask[i][j] = 1
            self.calc_mask = False
        self.frame = frame.data.astype(np.uint8)
        #print(np.shape(self.frame))
        img = self.frame
        self.shape = img.shape
        self.raw_data.emit(img)
        og_img = np.copy(img)
        if self.crosshairs:
            cv.circle(img, (int(img.shape[1] / 2) + self.x_offset, int(img.shape[0] / 2) + self.y_offset), self.radius,
                      (0, 0, 255), 2)
            cv.line(img, (0, int(img.shape[0] / 2) + self.y_offset),
                    (int(img.shape[1] / 2) - self.radius + self.x_offset, int(img.shape[0] / 2) + self.y_offset),
                    (0, 0, 255), 2)

            cv.line(img, (int(img.shape[1] / 2) + self.radius + self.x_offset, int(img.shape[0] / 2) + self.y_offset),
                    (int(img.shape[1]), int(img.shape[0] / 2) + self.y_offset), (0, 0, 255), 2)

            cv.line(img, (int(img.shape[1] / 2) + self.x_offset, 0),
                    (int(img.shape[1] / 2) + self.x_offset, int(img.shape[0] / 2) - self.radius + self.y_offset),
                    (0, 0, 255), 2)

            cv.line(img, (int(img.shape[1] / 2) + self.x_offset, int(img.shape[0] / 2) + self.y_offset + self.radius),
                    (int(img.shape[1] / 2) + self.x_offset, int(img.shape[0])), (0, 0, 255), 2)
            self.data_signal.emit(img)
            og_img[
            int(img.shape[0] / 2) - self.radius + self.y_offset:int(img.shape[0] / 2) + self.radius + self.y_offset,
            int(img.shape[1] / 2) - self.radius + self.x_offset:int(img.shape[1] / 2) + self.radius + self.x_offset, 0] \
                = og_img[int(img.shape[0] / 2) - self.radius + self.y_offset:int(
                img.shape[0] / 2) + self.radius + self.y_offset,
                  int(img.shape[1] / 2) - self.radius + self.x_offset:int(
                      img.shape[1] / 2) + self.radius + self.x_offset, 0] * self.mask
            og_img[
            int(img.shape[0] / 2) - self.radius + self.y_offset:int(img.shape[0] / 2) + self.radius + self.y_offset,
            int(img.shape[1] / 2) - self.radius + self.x_offset:int(img.shape[1] / 2) + self.radius + self.x_offset, 1] \
                = og_img[int(img.shape[0] / 2) - self.radius + self.y_offset:int(
                img.shape[0] / 2) + self.radius + self.y_offset,
                  int(img.shape[1] / 2) - self.radius + self.x_offset:int(
                      img.shape[1] / 2) + self.radius + self.x_offset, 1] * self.mask
            og_img[
            int(img.shape[0] / 2) - self.radius + self.y_offset:int(img.shape[0] / 2) + self.radius + self.y_offset,
            int(img.shape[1] / 2) - self.radius + self.x_offset:int(img.shape[1] / 2) + self.radius + self.x_offset, 2] \
                = og_img[int(img.shape[0] / 2) - self.radius + self.y_offset:int(
                img.shape[0] / 2) + self.radius + self.y_offset,
                  int(img.shape[1] / 2) - self.radius + self.x_offset:int(
                      img.shape[1] / 2) + self.radius + self.x_offset, 2] * self.mask
            self.ref_signal.emit(og_img[int(img.shape[0] / 2) - self.radius + self.y_offset:int(
                img.shape[0] / 2) + self.radius + self.y_offset,
                                 int(img.shape[1] / 2) - self.radius + self.x_offset:int(
                                     img.shape[1] / 2) + self.radius + self.x_offset, :])
        else:
            self.data_signal.emit(img)

    def frame_handler_two(self, frame):
        self.data_signal.emit(frame.astype(np.uint8))
        self.raw_data.emit(frame.astype(np.uint8))
        self.ref_signal.emit(frame.astype(np.uint8))

    def grabFrameCallback(self, hGrabber, pBuffer, framenumber, pData):
        Width = ctypes.c_long()
        Height = ctypes.c_long()
        BitsPerPixel = ctypes.c_int()
        colorformat = ctypes.c_int()

        self.ic.IC_GetImageDescription(hGrabber, Width, Height, BitsPerPixel, colorformat)

        bpp = int(BitsPerPixel.value / 8.0)
        buffer_size = Width.value * Height.value * bpp
        if buffer_size > 0:
            image = ctypes.cast(pBuffer, ctypes.POINTER(ctypes.c_ubyte * buffer_size))
            pData.data = np.ndarray(buffer=image.contents, dtype=np.uint8, shape=(Height.value, Width.value, bpp))
            #pData.data_signal.frame.emit(pData)
            if self.buffer_count == 0:
                self.frame_buffer = np.stack((self.frame_buffer, pData.data))
                self.buffer_count += 1
            elif self.buffer_count < self.frame_buffer_size:
                self.frame_buffer = np.append(self.frame_buffer, [pData.data], axis=0)
                self.buffer_count += 1
            else:
                if self.reset_buffer:
                    self.frame_buffer = [pData.data]
                    self.buffer_count = 1
                    self.reset_buffer = False
                else:
                    mean = np.mean(self.frame_buffer, axis = 0)
                    pData.data_signal.frame.emit(mean)
                    self.frame_buffer = np.delete(self.frame_buffer, 0, 0)
                    self.frame_buffer = np.append(self.frame_buffer, [pData.data], axis = 0)
                #self.buffer_count = 0







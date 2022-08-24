import cv2
import abc
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import ctypes
import os
import numpy as np

_devices = []

# If not on Windows, automatically in debug mode, as the camera will not work
debug = bool(os.environ.get("RANGER_DEBUG", "")) or os.name != 'nt'

if not debug:
    local_dir = os.path.abspath(os.path.dirname(__file__))
    ic = ctypes.cdll.LoadLibrary(os.path.join(local_dir, "tisgrabber/tisgrabber_x64.dll"))
    from autoz2.tisgrabber import old_tisgrabber as tis

    tis.declareFunctions(ic)
    ic.IC_InitLibrary(0)

    for i in range(ic.IC_GetDeviceCount()):
        _devices.append(ic.IC_GetUniqueNamefromList(i).decode('utf-8'))

    tis_loaded = True
else:
    print("Running in debug mode")
    tis_loaded = False


class SignalWrapper(QObject):
    newimage = pyqtSignal(object)


class CallbackUserdata(ctypes.Structure):
    signals = SignalWrapper()
    def __init__(self):
        super().__init__()
        self.frame = None

class BaseCamera(abc.ABC):
    fps: float

    @abc.abstractmethod
    def __init__(self, bridge, *args, **kwargs): ...
    @abc.abstractmethod
    def start(self): ...
    @abc.abstractmethod
    def stop(self): ...
    @abc.abstractmethod
    def set_framerate(self, fps: float = 1.0): ...


def get_camera_class():
    if debug:
        return EmulatedCamera
    else:
        return Camera

class Camera(BaseCamera):
    devices = _devices
    def __init__(self, bridge, *args, **kwargs):
        super().__init__(bridge, *args, **kwargs)
        self.hGrabber = ic.IC_CreateGrabber()
        self.connected = False
        self.playing = False
        self.connect()
        # Note: this wrapped callback MUST be connected to this object or it will go out of scope when this function
        # exits and cause a hidden segfault
        # Same goes for the user callback information.
        self.fn = ic.FRAMEREADYCALLBACK(self.grabFrameCallback)
        self.userCallbackData = bridge

        # Default Parameters
        self.color_profile = "RGB32"
        self.resolution = (1224, 1024)
        self.framerate = 70
        self._initialized = False

    def connect(self):
        # For some very annoying reason you also first need to call this or the GetUniqueNamefromList
        # function won't work.
        device_name = tis.D(ic.IC_GetUniqueNamefromList(0))
        print("Unique Name : {}".format(device_name))
        ic.IC_OpenDevByUniqueName(self.hGrabber, tis.T(device_name))
        if ic.IC_IsDevValid(self.hGrabber):
            self.connected = True
            print("connected to camera")
        else:
            print("Error connecting to device: ", device_name)

    def set_framerate(self, fps: float = 1.0):
        print("set fp stat")
        if self.playing:
            print("Stop Live")
            ic.IC_StopLive(self.hGrabber)
        print("change FPS")
        ic.IC_SetFrameRate(self.hGrabber, ctypes.c_float(fps))
        if self.playing:
            print("Start Live")
            ic.IC_StartLive(self.hGrabber, 0)

    def start(self):
        if not self._initialized:
            ic.IC_SetFrameReadyCallback(self.hGrabber, self.fn, self.userCallbackData)
            # 0 must be set here in order for frames to be copied into memory
            ic.IC_SetContinuousMode(self.hGrabber, 0)
            self._initialized = True
        # 1 = show, 0 = hide
        ic.IC_StartLive(self.hGrabber, 0)
        self.playing = True
        print("started camera")

    def stop(self):
        ic.IC_StopLive(self.hGrabber)
        self.playing = False

    def grabFrameCallback(self, hGrabber, pBuffer, framenumber, callback_userdata: CallbackUserdata):
        Width = ctypes.c_long()
        Height = ctypes.c_long()
        BitsPerPixel = ctypes.c_int()
        colorformat = ctypes.c_int()
        ic.IC_GetImageDescription(hGrabber, Width, Height, BitsPerPixel, colorformat)
        bpp = int(BitsPerPixel.value / 8.0)
        buffer_size = Width.value * Height.value * bpp
        if buffer_size > 0:
            image = ctypes.cast(pBuffer, ctypes.POINTER(ctypes.c_ubyte * buffer_size))
            data = np.ndarray(buffer=image.contents, dtype=np.uint8, shape=(Height.value, Width.value, bpp))
            callback_userdata.frame = data
            callback_userdata.signals.newimage.emit(data)


class EmulatedCamera(BaseCamera):
    """
    Implementation of the Camera interface that does nothing. Used for debugging / testing.
    """
    def __init__(self, bridge: CallbackUserdata):
        self.callback = bridge
        self.timer = QTimer()
        self.timer.timeout.connect(self.shit)
        self.timer.start(1*1000)

    def shit(self):
        # print("called")
        frame = np.zeros(shape=(1024//4, 1224//4, 3), dtype=np.uint8)
        self.callback.frame = frame
        self.callback.signals.newimage.emit(frame)

    def start(self):
        ...
    def stop(self):
        ...
    def set_framerate(self, fps: float = 1.0):
        ...


class ReplayCamera(BaseCamera):
    """
    Camera that plays back a previous recording.
    This should be run in a separate thread and accessed the same as the other cameras.
    """
    def __init__(self, bridge: CallbackUserdata, path="", loop=True):
        self.cur_video_frame_index = None
        self.cur_video_n_frames = None
        self.bridge = bridge
        self.videoHandle = None
        self.fps = 0

        if path:
            self.open(path)
        # Convert fps to a sleep interval. Note: this currently assumes FPS is constant. It should be possible
        # to convert this to dynamic FPS.
        self.frame: np.ndarray = np.ndarray([])
        self.between_frame_timer = QTimer()
        self.between_frame_timer.timeout.connect(self.get_next_frame)
        self.playing = False
        self.loop = loop


    def start(self):
        if not self.videoHandle:
            print("ERROR: Need to open a file before starting playback")
            return
        if not self.fps:
            print("ERROR: FPS has not been set correctly")
            return
        self.between_frame_timer.start(1/self.fps * 1000)  # NB. fps is in s, timer works in milliseconds
        self.playing = True

    def get_next_frame(self):
        # TODO: probably better to use milliseconds into video rather than frame number in case of dynamic fps
        self.videoHandle.set(cv2.CAP_PROP_POS_FRAMES, self.cur_video_frame_index-1)
        err, img = self.videoHandle.read()
        # self.cur_video_frame_index += 1

        if self.cur_video_frame_index == self.cur_video_n_frames:
            if self.loop:
                self.cur_video_frame_index = 0
            else:
                self.stop()
                return

        if img is None:
            # TODO: fix perpetual increment
            print("ERROR: Got 'None' trying to read from video")
            return

        self.frame = img
        self.bridge.frame = img
        self.bridge.signals.newimage.emit(img)


    def stop(self):
        self.playing = False
        self.between_frame_timer.stop()

    def set_framerate(self, fps: float = 1.0):
        self.fps = fps

    def open(self, path):
        if not os.path.exists(path):
            raise RuntimeError(f"Video does not exist: {path}")
        self.videoHandle = cv2.VideoCapture(path)
        video_native_fps = self.videoHandle.get(cv2.CAP_PROP_FPS)
        video_native_fps = 6
        self.cur_video_n_frames = self.videoHandle.get(cv2.CAP_PROP_FRAME_COUNT)
        self.cur_video_frame_index = 0
        print("video native fps", video_native_fps)
        self.set_framerate(video_native_fps)

    @property
    def resolution(self):
        return self.frame.shape

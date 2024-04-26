import cv2
import numpy as np
import time
from typing import Literal, List, Tuple, get_args

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory
import threading

"""
    Camera class based on thread
    It allows to start camera with specified resolution and FPS
"""
class Camera(threading.Thread):
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        resolution: Tuple[int, int],
        fps: float = 30,
    ):
        super().__init__()

        # camera parameters
        self._device = device
        self._resolution = resolution
        self._fps = fps

        # camera1
        self._cap = cv2.VideoCapture(f"/dev/video{self._device}", cv2.CAP_V4L2)
        self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
        self._cap.set(cv2.CAP_PROP_FPS, self._fps)

        # data
        self._frame: np.ndarray = None
        self._grabbed = False

        # performance
        self._ctime = 0
        self._ptime = 0
        self._real_fps = 0

    @property
    def ready(self):
        return self._cap.isOpened()

    @property
    def frame_ok(self):
        return self._grabbed

    @property
    def resolution(self):
        return self._resolution

    @property
    def fps(self):
        return self._real_fps

    @property
    def frame(self):
        return self._frame

    @property
    def shape(self):
        return self._frame.shape

    @property
    def size(self):
        return self._frame.nbytes

    def run(self):
        while self._cap.isOpened():
            # grab frame
            self._grabbed, self._frame = self._cap.read()

            # calculate fps
            self._ctime = time.time()
            self._real_fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime
            print(self._real_fps)


"""
    Sample camera class.
    It allows to start camera with specified resolution and FPS
"""
#class Camera():
##class Camera(multiprocessing.Process):
#    def __init__(
#        self,
#        device: int, # 1 for /dev/video1
#        resolution: Tuple[int, int],
#        fps: float = 30,
#        name: str = "camera"
#    ):
#        #super().__init__()
#        # camera parameters
#        self._device = device
#        self._resolution = resolution
#        self._fps = fps
#
#        # OpenCV capture parameters
#        #self._gst_shm = (
#        #    f"gst-launch-1.0 shmsrc socket-path=/tmp/cam1 ! "
#        #    f"image/jpeg,width=1280,height=720,framerate=30/1 ! "
#        #    f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
#        #)
#        #self._cap = cv2.VideoCapture(self._gst_shm, cv2.CAP_GSTREAMER)
#        self._gst_cmd = (
#            f"gst-launch-1.0 v4l2src device=/dev/video{self._device} ! "
#            f"image/jpeg,width={self._resolution[0]},height={self._resolution[1]},framerate={self._fps}/1 ! "
#            f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
#        )
#        self._cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)
#        #self._cap = cv2.VideoCapture(f"/dev/video{self._device}", cv2.CAP_V4L2)
#        #self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
#        #self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
#        #self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
#        #self._cap.set(cv2.CAP_PROP_FPS, self._fps)
#
#        # performance metrics
#        self._ctime = 0
#        self._ptime = 0
#        self._actual_fps = 0
#
#        # data
#        self._memory = name
#        self._frame_shape = (self._resolution[1], self._resolution[0], 3)
#        self._frame = np.full(self._frame_shape, np.uint8)
#        self._frame_size = self._frame.nbytes
#
#    @property
#    def device(self):
#        return self._device
#
#    @property
#    def ready(self):
#        return self._cap.isOpened()
#
#    @property
#    def resolution(self):
#        return self._resolution
#
#    @property
#    def fps(self):
#        return self._actual_fps
#
#    @property
#    def gst(self):
#        return self._gst_cmd
#
#    @property
#    def name(self):
#        return self._memory
#
#    @property
#    def shape(self):
#        return self._frame_shape
#
#    @property
#    def size(self):
#        return self._frame_size
#
#    @property
#    def frame(self):
#        return self._frame
#
#    @property
#    def cap(self):
#        return self._cap
#
#    def run(self):
#        # get shared memory object
#        shm = shared_memory.SharedMemory(create=True, size=self._frame_size, name=self._memory)
#        buffer = np.ndarray(self._frame_shape, dtype=np.uint8, buffer=shm.buf)
#
#        # run capture into the buffer
#        if not self._cap.isOpened():
#            print("Failed to open capture")
#            # TODO: RaiseError
#            exit()
#
#        while self._cap.isOpened():
#            # read frames
#            ret, frame = self._cap.read()
#            if ret:
#                # put frame to the buffer
#                np.copyto(buffer, frame)
#
#                # calculate fps
#                self._ctime = time.time()
#                self._actual_fps = 1/(self._ctime-self._ptime)
#                self._ptime = self._ctime
#                print(self._actual_fps)
#
#        # capture fail
#        self._cap.release()
#        shm.close()
#        shm.unlink()
        
# demo code to run this separately
if __name__ == "__main__":
    test_cam1 = Camera(device=0, resolution=(1280, 720))
    test_cam1.start()

    test_cam2 = Camera(device=2, resolution=(1280, 720))
    test_cam2.start()

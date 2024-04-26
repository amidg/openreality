import cv2
import numpy as np
import time
from typing import Tuple
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

# demo code to run this separately
if __name__ == "__main__":
    test_cam1 = Camera(device=0, resolution=(1280, 720))
    test_cam1.start()

    test_cam2 = Camera(device=2, resolution=(1280, 720))
    test_cam2.start()

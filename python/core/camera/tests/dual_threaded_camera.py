import cv2
import numpy as np
import time
from typing import Literal, List, Tuple, get_args

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory
import threading

class DualCamera():
    def __init__(
        self,
    ):
        #super().__init__()

        # camera parameters
        self._resolution = (1280, 720)
        self._fps = 30

        # camera1
        self._cap1 = cv2.VideoCapture(f"/dev/video0", cv2.CAP_V4L2)
        self._cap1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._cap1.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
        self._cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
        self._cap1.set(cv2.CAP_PROP_FPS, self._fps)

        # camera2
        self._cap2 = cv2.VideoCapture(f"/dev/video2", cv2.CAP_V4L2)
        self._cap2.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._cap2.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
        self._cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
        self._cap2.set(cv2.CAP_PROP_FPS, self._fps)

        # data
        self._frame_left: np.ndarray = None
        self._left_ready = False
        self._frame_right: np.ndarray = None
        self._right_ready = False

        # stream
        left_stream = threading.Thread(target=self._left_cam_read)
        left_stream.start()

        right_stream = threading.Thread(target=self._right_cam_read)
        right_stream.start()

        # performance
        self._ctime_left = 0
        self._ptime_left = 0
        self._fps_left = 0

        self._ctime_right = 0
        self._ptime_right = 0
        self._fps_right = 0

    def _left_cam_read(self):
        while True:
            self._left_ready, self._frame_left = self._cap1.read()

            # calculate fps
            self._ctime_left = time.time()
            self._fps_left = 1/(self._ctime_left-self._ptime_left)
            self._ptime_left = self._ctime_left

    def _right_cam_read(self):
        while True:
            self._right_ready, self._right_frame = self._cap2.read()

            # calculate fps
            self._ctime_right = time.time()
            self._fps_right = 1/(self._ctime_right-self._ptime_right)
            self._ptime_right = self._ctime_right

    def run(self):
        while True:
            print(f"FPS: LEFT {self._fps_left} / RIGHT {self._fps_right}")

        
# demo code to run this separately
if __name__ == "__main__":
    dual_camera = DualCamera()
    dual_camera.run()

import cv2
import numpy as np
import time
from typing import Tuple
import threading
from enum import Enum

"""
    Camera class designed to read camera using Jetson API
    It allows to start camera with specified resolution and FPS
"""
class Camera():
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        resolution: Tuple[int, int],
        crop_area: Tuple[int, int, int, int], # y0,y1,x0,x1
        fps: float = 30
    ):
        # camera parameters
        self._device = device
        self._resolution = resolution
        self._crop_area = crop_area 
        self._fps = fps

        # data
        self._frame: np.ndarray = None
        self._grabbed = False

        # performance
        self._ctime = 0
        self._ptime = 0
        self._real_fps = 0

        # start capture
        self._gst_cmd = (
            f"nvarguscamerasrc sensor-id={self._device} ! "
            f"video/x-raw(memory:NVMM),"
            f"width={self._resolution[0]}, height={self._resolution[1]}, "
            f"format=(string)NV12, framerate{self._fps}/1 ! "
            f"nvvidconv ! " # you can add rotation here
            f"video/x-raw,format=(string)BGR,"
            f"width={self._resolution[0]}, height={self._resolution[1]},"
            f"appsink max-buffers=1 drop=True"
        )
        self._cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)

    @property
    def opened(self):
        return self._cap.isOpened()

    @property
    def frame_ready(self):
        return self._cap.grab()

    @property
    def cap(self):
        return self._cap

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
    def test_frame(self):
        self._frame = np.full((self._resolution[1], self._resolution[0], 3), np.uint8)
        self._frame = self._frame[
            self._crop_area[0]:self._crop_area[1],
            self._crop_area[2]:self._crop_area[3]
        ]
        return self._frame

    @property
    def frame(self):
        # get frame
        ret, self._frame = self._cap.retrieve(0)
        self._frame = self._frame[
            self._crop_area[0]:self._crop_area[1],
            self._crop_area[2]:self._crop_area[3]
        ]

        # calculate fps
        self._ctime = time.time()
        self._real_fps = 1/(self._ctime-self._ptime)
        self._ptime = self._ctime

        self._grabbed = ret
        return self._frame

    @property
    def shape(self):
        return self._frame.shape

    @property
    def size(self):
        return self._frame.nbytes

# demo code to run this separately
if __name__ == "__main__":
    # camera setup
    crop_area = (0,720,320,960) # y0,y1,x0,x1
    resolution = (1920,1080)
    cam_left = Camera(device=0, resolution=resolution, crop_area=crop_area)

    # window
    cv2.namedWindow("render", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # capture
    while True:
        # get frame
        if cam_left.frame_ready:
            frame = cam_left.frame

        # render window
        print(cam_left.fps)
        cv2.imshow("render", frame)    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam_left.release()
    cv2.destroyAllWindows()

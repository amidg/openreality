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
        crop_area: Tuple[int, int, int, int], # y0,y1,x0,x1
        fps: float = 30,
    ):
        super().__init__()

        # camera parameters
        self._device = device
        self._resolution = resolution
        self._crop_area = crop_area 
        self._fps = fps

        # camera
        self._gst_cmd = (
            f"gst-launch-1.0 v4l2src device=/dev/video{self._device} ! "
            f"image/jpeg,width={self._resolution[0]},height={self._resolution[1]},framerate={self._fps}/1 ! "
            f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
        )
        self._cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)
        #self._cap = cv2.VideoCapture(f"/dev/video{self._device}", cv2.CAP_V4L2)
        #self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        #self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
        #self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
        #self._cap.set(cv2.CAP_PROP_FPS, self._fps)

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
            ret, self._frame = self._cap.read()
            if not ret:
                # TODO: add error checking
                continue

            # crop area
            # TODO: add error checking
            self._frame = self._frame[
                self._crop_area[0]:self._crop_area[1],
                self._crop_area[2]:self._crop_area[3]
            ]
            self._grabbed = ret

            # calculate fps
            self._ctime = time.time()
            self._real_fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime

# demo code to run this separately
if __name__ == "__main__":
    crop_area = (0,720,320,960)
    resolution = (1280,720)
    test_cam1 = Camera(device=3, resolution=resolution, crop_area=crop_area)
    test_cam1.start()

    #test_cam2 = Camera(device=3, resolution=resolution, crop_area=crop_area)
    #test_cam2.start()

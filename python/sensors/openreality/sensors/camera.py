import cv2
import numpy as np
import time
from typing import Tuple
import threading
from enum import Enum

"""
    Camera class allows to capture from shm device
    This is system agnostic and can be used for any hardware
"""
class Camera():
    def __init__(
        self,
        device: int, # device, e.g. 0 for /dev/video0
        resolution: Tuple[int, int],
        crop_area: Tuple[int, int, int, int], # y0,y1,x0,x1
        fps: int = 30
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
            f"video/x-raw(memory:NVMM), "
            f"width=(int){self._resolution[0]}, height=(int){self._resolution[1]}, "
            f"format=(string)NV12, framerate=(fraction){self._fps}/1 ! "
            f"nvvidconv flip-method=0 "
            f"top={self._crop_area[0]} bottom={self._crop_area[1]} left={self._crop_area[2]} right={self._crop_area[3]} ! "
            f"video/x-raw, format=(string)BGRx, "
            f"width=(int){self._crop_area[1] - self._crop_area[0]}, height=(int){self._crop_area[3] - self._crop_area[2]} ! "
            f"videoconvert ! video/x-raw, format=(string)BGR ! "
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
    def frame(self):
        # get frame
        ret, self._frame = self._cap.retrieve(0)

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
def main():
    # camera setup
    crop_area = (0,1440,0,1280) # y0,y1,x0,x1
    resolution = (3264,1848)
    cam_left = Camera(
        device=0,
        resolution=resolution,
        crop_area=crop_area
    )

    # window
    cv2.namedWindow("render", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # capture
    while cam_left.opened:
        # get frame
        if cam_left.frame_ready:
            # get frame
            frame = cam_left.frame
            cv2.imshow("render", frame)    
            # show fps
            print(cam_left.fps)

        # break if necessary
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam_left.cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

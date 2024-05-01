import cv2
import numpy as np
import time
from typing import Tuple
import threading
from enum import Enum

class DeviceType(Enum):
    V4L2 = 1
    GST = 2
    JETSON = 3 # nvidia specific hardware acceleration

"""
    Camera class based on thread
    It allows to start camera with specified resolution and FPS
"""
class Camera():
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        resolution: Tuple[int, int],
        crop_area: Tuple[int, int, int, int], # y0,y1,x0,x1
        fps: float = 30,
        driver: DeviceType = DeviceType.V4L2
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
        self._cap: cv2.VideoCapture = None
        if driver == DeviceType.V4L2:
            # V4L2 is more resource friendly because it does not spawn another gst process inside it
            # use it for non-Nvidia devices
            self._cap = cv2.VideoCapture(f"/dev/video{self._device}", cv2.CAP_V4L2)
            self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
            self._cap.set(cv2.CAP_PROP_FPS, self._fps)
        elif driver == DeviceType.GST:
            self._gst_cmd = (
                f"gst-launch-1.0 v4l2src device=/dev/video{self._device} ! "
                f"image/jpeg,width={self._resolution[0]},height={self._resolution[1]},framerate={self._fps}/1 ! "
                f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
            )
            self._cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)
        elif driver == DeviceType.JETSON:
            RaiseError("Jetson not implemented yet, bye :)")

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
    resolution = (1280,720)
    cam_left = Camera(device=3, resolution=resolution, crop_area=crop_area)

    # window
    #cv2.namedWindow("render", cv2.WINDOW_NORMAL)
    #cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # capture
    while True:
        # get frame
        if cam_left.frame_ready:
            frame = cam_left.frame

        # render window
        print(cam_left.fps)
        #cv2.imshow("render", frame)    
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

    cam_left.release()
    cv2.destroyAllWindows()

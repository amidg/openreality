import cv2
import numpy as np
import time
from typing import Tuple
import threading
from enum import Enum

from openreality.sensors.cameras.imx219 import imx219

"""
    Camera class allows to capture from shm device
    This is system agnostic and can be used for any hardware
"""
class StereoCamera():
    def __init__(
        self,
        device_left: int, # device, e.g. 0 for /dev/video0
        device_right: int, # device, e.g. 0 for /dev/video0
        config: Tuple[int, int, int], # width, height, fps
        target_resolution: Tuple[int, int], # width, height 
        rotation: int = 0 # corresponds to the nvvidconv flip-method
    ):
        # camera parameters
        self._device_left = device_left
        self._device_right = device_right
        self._resolution = (config[0], config[1])
        self._fps = config[2]
        self._target_resolution = target_resolution
        """
            flip-method: video flip methods
                (0): none             - Identity (no rotation)
                (1): counterclockwise - Rotate counter-clockwise 90 degrees
                (2): rotate-180       - Rotate 180 degrees
                (3): clockwise        - Rotate clockwise 90 degrees
                (4): horizontal-flip  - Flip horizontally
                (5): upper-right-diagonal - Flip across upper right/lower left diagonal
                (6): vertical-flip    - Flip vertically
                (7): upper-left-diagonal - Flip across upper left/lower right diagonal
        """
        self._rotation = rotation
        """
            crop_area is auto-determined. It is based on the following:
            - current camera resolution
            - desired resolution aspect ratio
            This allows to avoid "zooming" effect of the smartphone camera
        """
        aspect_ratio = (self._target_resolution[0]/2)/self._target_resolution[1]
        new_height = self._resolution[1]
        new_width = int(aspect_ratio*new_height)
        if new_width > self._resolution[0]:
            # technically this might violate the aspect ratio
            new_width = self._resolution[0]
            new_height = int(new_width/aspect_ratio)
        self._crop_area = ( # y0,y1,x0,x1 (top,bottom,left,right)
            # y0, top
            int((self._resolution[1] - new_height)/2),
            # y1, bottom 
            int(self._resolution[1] - (self._resolution[1] - new_height)/2),
            # x0, left
            int((self._resolution[0] - new_width)/2),
            # x1, right
            int(self._resolution[0] - (self._resolution[0] - new_width)/2),
        )
        print(apsect_ratio)
        print(self._crop_area)

        # data
        self._frame: np.ndarray = None
        self._grabbed = False

        # performance
        self._ctime = 0
        self._ptime = 0
        self._real_fps = 0

        # start capture
        self._gst_cmd = (
            # compositor and appsink
            f"nvcompositor name=comp "
            f"background-w={self._target_resolution[0]}  background-h={self._target_resolution[1]} "
            f"sink_0::xpos=0 sink_0::ypos=0 "
            f"sink_0::width={self._crop_area[3] - self._crop_area[2]} "
            f"sink_0::height={self._crop_area[1] - self._crop_area[0]} "
            f"sink_1::xpos={self._crop_area[3] - self._crop_area[2]} sink_1::ypos=0 "
            f"sink_1::width={self._crop_area[3] - self._crop_area[2]} "
            f"sink_1::height={self._crop_area[1] - self._crop_area[0]} ! "
            f"video/x-raw(memory:NVMM),format=(string)RGBA ! "
            f"nvvidconv ! video/x-raw,format=BGRx ! "
            f"videoconvert ! video/x-raw,format=BGR ! appsink max-buffers=1 drop=True "
            # camera left
            f"nvarguscamerasrc sensor-id={self._device_left} ! "
            f"video/x-raw(memory:NVMM), width=(int){self._resolution[0]}, height=(int){self._resolution[1]}, "
            f"format=(string)NV12, framerate=(fraction){self._fps}/1 ! "
            f"nvvidconv flip-method={self._rotation} "
            f"top=(int){self._crop_area[0]} bottom=(int){self._crop_area[1]} left=(int){self._crop_area[2]} right=(int){self._crop_area[3]} ! "
            f"video/x-raw(memory:NVMM),format=RGBA,width=(int){self._target_resolution[0]/2},height={self._target_resolution[1]} ! comp.sink_0 "
            # camera right
            f"nvarguscamerasrc sensor-id={self._device_right} ! "
            f"video/x-raw(memory:NVMM), width=(int){self._resolution[0]}, height=(int){self._resolution[1]}, "
            f"format=(string)NV12, framerate=(fraction){self._fps}/1 ! "
            f"nvvidconv flip-method={self._rotation} "
            f"top=(int){self._crop_area[0]} bottom=(int){self._crop_area[1]} left=(int){self._crop_area[2]} right=(int){self._crop_area[3]} ! "
            f"video/x-raw(memory:NVMM),format=RGBA,width=(int){self._target_resolution[0]/2},height={self._target_resolution[1]} ! comp.sink_1 "
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
    def gst_cmd(self):
        return self._gst_cmd

    @property
    def frame(self):
        # get frame
        self._grabbed, self._frame = self._cap.retrieve(0)

        # calculate fps
        self._ctime = time.time()
        self._real_fps = 1/(self._ctime-self._ptime)
        self._ptime = self._ctime
        return self._frame

    @property
    def shape(self):
        return self._frame.shape

    @property
    def size(self):
        return self._frame.nbytes

# demo code to run this separately
def main():
    # TODO: make camera setup a dynamic configuration
    camera_mode = imx219[1].parameters # Tuple(width, height, fps)
    stereo_camera = StereoCamera(
        device_left=0,
        device_right=1,
        config=camera_mode, # Tuple(width,height,fps)
        target_resolution=(2560,1440), # per entire frame, means both eyes next to each other
        rotation=2 # flip 180
    )

    # window
    cv2.namedWindow("render", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # capture
    while stereo_camera.opened:
        # get frame
        if stereo_camera.frame_ready:
            # get frame
            frame = stereo_camera.frame
            cv2.imshow("render", frame)
            # show fps
            print(stereo_camera.fps)

        # break if necessary
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stereo_camera.cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

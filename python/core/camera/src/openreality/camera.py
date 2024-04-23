import argparse
import cv2
import numpy as np
import os
from time import time

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

from typing import Literal, get_args

"""
    Sample camera class.
    This class runs a multiprocessing.Process and streams image from the camera device, usually /dev/videoX to the shared memory.
    This shared memory object can be accessed by other python programs
"""
class Camera(multiprocessing.Process):
    _ROTATION_TYPES = Literal[cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        width: int = 1920,
        height: int = 1080,
        fps: float = 30,
        rotation: _ROTATION_TYPES = None # cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE
    ):
        super().__init__()
        self._device = device
        self._memory = f"/tmp/cam{device}"
        self._width = width
        self._height = height
        self._fps = fps
        self._rotation = None
        if rotation is not None:
            options = get_args(_ROTATION_TYPES)
            try:
                assert rotation in _ROTATION_TYPES
                self._rotation = rotation
            except AssertionError:
                # TODO: add logger handler
                print(f"Incorrect rotation requested {rotation}: must be cv2.ROTATE_XX_YY type")

        # shared memory device
        # TODO: make frame and shm parameters programmatic, 3*8 is color depth 24bit
        self._gst_cmd = f"appsrc ! videoconvert ! shmsink socket-path={self._memory} sync=true wait-for-connection=false"
         

    def run(self):
        # create capture device
        cap = cv2.VideoCapture(self._device)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap.set(cv2.CAP_PROP_FPS, self._fps)

        # shared device
        shm = cv2.VideoWriter(self._gst_cmd, 0, self._fps, (self._width, self._height), True)

        # check if device is opened
        # TODO: add proper error checking
        if cap.isOpened() is not True:
            print("Cannot open camera. Exiting.")
            quit()

        # stream image
        while True:
            # Get the frame
            ret, frame = cap.read()
            # Check
            if ret is True:
                # Flip frame if necessary
                if self._rotation is not None:
                    frame = cv2.rotate(frame, self._rotation)
                # write to shared memory
                shm.write(frame)
            else:
                # TODO: logging handler
                print("camera capture failed")
        # stop opencv stream
        cap.release()

        
# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam_left = Camera(device=0)
    test_cam_right = Camera(device=1)
    test_cam_left.start()
    test_cam_right.start()

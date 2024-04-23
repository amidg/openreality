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
        self._memory = f"cam{device}"
        self._width = width
        self._height = height
        self._fps = fps
        self._rotation = None
        if rotation is not None:
            try:
                assert rotation in get_args(self._ROTATION_TYPES)
                self._rotation = rotation
            except AssertionError:
                # TODO: add logger handler
                print(f"Incorrect rotation requested {rotation}: must be cv2.ROTATE_XX_YY type")

        # shared memory device
        # TODO: make frame and shm parameters programmatic, 3*8 is color depth 24bit
        #self._shm = shared_memory.SharedMemory(
        #    create=True,
        #    name=self._memory,
        #    size=int(self._width*self._height*3*8)
        #)
        #if self._rotation == cv2.ROTATE_90_CLOCKWISE or self._rotation == cv2.ROTATE_90_COUNTERCLOCKWISE:
        #    self._frame = np.ndarray(
        #        (self._width, self._height, 3),
        #        dtype=np.dtypes.UInt8DType,
        #        buffer=self._shm.buf
        #    )
        #else:
        #    self._frame = np.ndarray(
        #        (self._height, self._width, 3),
        #        dtype=np.dtypes.UInt8DType,
        #        buffer=self._shm.buf
        #    )
        ## ready to go
        #print(f"Shared Memory is ready @ {self._shm.name}")

    def run(self):
        # create capture device
        cap = cv2.VideoCapture(self._device, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap.set(cv2.CAP_PROP_FPS, self._fps)

        # create frame for shared memory access
        if cap.isOpened():
            ret, frame = cap.read() # get test frame to create shared memory object
            if not ret:
                exit()
            # Flip frame if necessary
            if self._rotation is not None:
                frame = cv2.rotate(frame, self._rotation)
            shm = shared_memory.SharedMemory(
                create=True, size=frame.nbytes, name=self._memory
            )
            frame_shared = np.ndarray(frame.shape, dtype=frame.dtype, buffer=shm.buf)
        else:
            exit()

        # stream video
        # TODO: add handler when closed
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip frame if necessary
            if self._rotation is not None:
                frame = cv2.rotate(frame, self._rotation)
            np.copyto(frame_shared, frame)  # Copy frame to shared memory

        # stop opencv stream
        cap.release()
        shm.close()
        shm.unlink()

        
# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam_left = Camera(device=0, rotation=cv2.ROTATE_90_CLOCKWISE)
    test_cam_left.start()
    test_cam_right = Camera(device=1, rotation=cv2.ROTATE_90_CLOCKWISE)
    test_cam_right.start()

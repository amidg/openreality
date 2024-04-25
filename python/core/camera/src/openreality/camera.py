import argparse
import cv2
import numpy as np
import os
import time

# multiprocessing
import subprocess
import multiprocessing
from multiprocessing import shared_memory
import queue
from typing import Literal, List, Tuple, get_args

ROTATION_TYPES = Literal[
    cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180,
    cv2.ROTATE_90_COUNTERCLOCKWISE
]

"""
    Sample camera class.
    It allows to start camera with specified resolution and FPS
"""
class Camera(multiprocessing.Process):
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        resolution: Tuple[int, int],
        fps: float = 30
    ):
        super().__init__()

        # camera parameters
        self._device = device
        self._resolution = resolution
        self._fps = fps

        # OpenCV capture parameters
        self._gst_cmd = (
            f"gst-launch-1.0 v4l2src device=/dev/video{self._device} ! "
            f"image/jpeg,width={self._resolution[0]},height={self._resolution[1]},framerate={self._fps}/1 ! "
            f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
        )

        print(self._gst_cmd)

        # performance metrics
        self._ctime = 0
        self._ptime = 0
        self._actual_fps = 0

        # data
        self._memory = f"camera{self._device}"
        self._frame_shape = (self._resolution[1], self._resolution[0], 3)
        self._frame_size = np.full(self._frame_shape, np.uint8).nbytes

    @property
    def device(self):
        return self._device

    @property
    def fps(self):
        return self._actual_fps

    def run(self):
        # camera
        cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)

        # get shared memory object
        shm = shared_memory.SharedMemory(create=True, size=self._frame_size, name=self._memory)
        buffer = np.ndarray(self._frame_shape, dtype=np.uint8, buffer=shm.buf)

        # debug window
        cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # run capture into the buffer
        if not cap.isOpened():
            print("Failed to open capture")
            exit()

        while cap.isOpened():
            # read frames
            ret, frame = cap.read()
            if ret:
                # put frame to the buffer
                np.copyto(buffer, frame)

                # calculate fps
                self._ctime = time.time()
                self._actual_fps = 1/(self._ctime-self._ptime)
                self._ptime = self._ctime
                print(self._actual_fps)

                # debug
                cv2.imshow("render", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        # capture fail
        cap.release()
        shm.close()
        shm.unlink()
        
# demo code to run this separately
if __name__ == "__main__":
    # test cam
    cam_left = Camera(device=0, resolution=(1920, 1080))
    cam_left.start()

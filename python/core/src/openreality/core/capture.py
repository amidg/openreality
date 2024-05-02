import cv2
import numpy as np
import time
from typing import Literal, List, Dict, Tuple, Union, get_args

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory
import queue
import threading

# openreality
from openreality.sensors.camera import Camera

ROTATION_TYPES = Literal[
    cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180,
    cv2.ROTATE_90_COUNTERCLOCKWISE
]

"""
   Capture class that combines camera stream from N cameras into one buffer 
"""
class Capture(threading.Thread):
    def __init__(self, cameras: List[Camera], rotation: ROTATION_TYPES = None):
        # do some setup
        super().__init__()
        self._left_cam = cameras[0]
        self._right_cam = cameras[1]
        self._rotation = None
        if rotation is not None:
            try:
                assert rotation in get_args(ROTATION_TYPES)
                self._rotation = rotation
            except AssertionError:
                # TODO: add logger handler
                print(f"Incorrect rotation requested {rotation}: must be cv2.ROTATE_XX_YY type")

        # time
        self._ctime = 0
        self._ptime = 0
        self._fps = 0

        # data
        self._frame = None
        self._frame_buffer = queue.SimpleQueue()
        self._memory = "/capture"

        # create render buffer from two front cameras
        frame_left = self._left_cam.test_frame
        frame_right = self._right_cam.test_frame
        self._shm = shared_memory.SharedMemory(
            create=True,
            size=(frame_left.nbytes+frame_right.nbytes),
            name=self._memory
        )
        render_shape = tuple([frame_right.shape[0] + frame_left.shape[0], frame_left.shape[1], frame_left.shape[2]])
        if self._rotation in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]:
            render_shape = tuple([frame_right.shape[1] + frame_left.shape[1], frame_left.shape[0], frame_left.shape[2]])
        self._shm_frame_buffer = np.ndarray(
            render_shape,
            dtype=np.uint8,
            buffer=self._shm.buf
        )

        # left cam thread
        self._left_buffer = queue.Queue(maxsize=10)
        self._left_thread = threading.Thread(target=self._left_capture)
        self._left_thread.start()

        # right cam thread
        self._right_buffer = queue.Queue(maxsize=10)
        self._right_thread = threading.Thread(target=self._right_capture)
        self._right_thread.start()

    @property
    def frame(self):
        return self._frame_buffer.get()

    @property
    def buffer_ready(self):
        return not self._frame_buffer.empty()

    @property
    def fps(self):
        return self._fps

    # supporting functions
    def _flush_buffer(self):
        while not self._frame_buffer.empty():
            self._frame_buffer.get_nowait()

    # camera threads
    def _left_capture(self):
        frame = None
        while True:
            if self._left_cam.frame_ready:
                frame = self._left_cam.frame
                if self._rotation is not None:
                    frame = cv2.rotate(frame, self._rotation)
                self._left_buffer.put(frame)

    def _right_capture(self):
        frame = None
        while True:
            if self._right_cam.frame_ready:
                frame = self._right_cam.frame
                if self._rotation is not None:
                    frame = cv2.rotate(frame, self._rotation)
                self._right_buffer.put(frame)

    # main capture thread
    def run(self):
        # wait for all cams to start
        while not (self._left_cam.opened and self._right_cam.opened):
            print("waiting to start cameras")

        # stream video to renderer
        while True:
            # if buffer is empty, we need to wait until there are frames to use
            if self._left_buffer.empty() or self._right_buffer.empty():
                continue

            # build rendered frame
            self._frame = np.vstack(tuple([self._right_buffer.get(), self._left_buffer.get()]))
            self._frame_buffer.put(self._frame)
            np.copyto(self._shm_frame_buffer, self._frame)

            # calculate fps
            self._ctime = time.time()
            self._fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime
            print(f"FPS Capture / Left / Right: {self._fps} / {self._left_cam.fps} / {self._right_cam.fps}")

            # empty queue to avoid RAM overflow
            if self._frame_buffer.qsize() > 100:
                self._flush_buffer()
        
# demo code to run this separately
if __name__ == "__main__":
    # start create list of cameras
    crop_area = (0,720,320,960)
    resolution = (1280,720)
    cam_left = Camera(device=3, resolution=resolution, crop_area=crop_area)
    cam_right = Camera(device=1, resolution=resolution, crop_area=crop_area)
    cameras = [cam_left, cam_right]

    # create capture session
    # There is no need to start cameras one by one because when object is created, capture is automatically started
    capture = Capture(cameras=cameras, rotation=cv2.ROTATE_90_CLOCKWISE)
    capture.start()

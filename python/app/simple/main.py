import cv2
import cupy as cp
import numpy as np
import time
from typing import List, Dict, Tuple, Union

# multiprocessing
import multiprocessing
import queue
import threading
from enum import Enum, EnumMeta

# openreality
from openreality.sensors.camera import Camera

class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True

class BaseEnum(Enum, metaclass=MetaEnum):
    pass

class CameraRotation(BaseEnum):
    ROTATE_90_CW = cv2.ROTATE_90_CLOCKWISE
    ROTATE_180 = cv2.ROTATE_180
    ROTATE_90_CCW = cv2.ROTATE_90_COUNTERCLOCKWISE

"""
   Capture class that combines camera stream from N cameras into one buffer 
"""
class Capture(threading.Thread):
    def __init__(self, cameras: List[Camera], rotation: CameraRotation = None):
        # do some setup
        super().__init__()
        self._left_cam = cameras[0]
        self._right_cam = cameras[1]
        self._rotation = None
        if rotation is not None:
            try:
                assert rotation in CameraRotation 
                self._rotation = rotation.value # enum needs value
            except AssertionError:
                # TODO: add logger handler
                print(f"Incorrect rotation requested {rotation}")

        # time
        self._ctime = 0
        self._ptime = 0
        self._fps = 0

        # data
        self._frame = None
        self._frame_buffer = queue.Queue()

        # left cam thread
        #self._left_buffer = queue.Queue(maxsize=50)
        #self._left_thread = threading.Thread(target=self._left_capture)
        #self._left_thread.start()

        ## right cam thread
        #self._right_buffer = queue.Queue(maxsize=50)
        #self._right_thread = threading.Thread(target=self._right_capture)
        #self._right_thread.start()
        

    @property
    def frame(self):
        return self._frame
        #return self._frame_buffer.get()

    @property
    def ready(self):
        return np.any(self._frame)
        #return not self._frame_buffer.empty()

    @property
    def fps(self):
        return self._fps

    # supporting functions
    def _flush_buffer(self):
        while not self._frame_buffer.empty():
            self._frame_buffer.get_nowait()

    # camera threads
    def _left_capture(self):
        while True:
            if self._left_cam.frame_ready:
                frame = self._left_cam.frame
                if self._rotation is not None:
                    frame = cv2.rotate(frame, self._rotation)
                self._left_buffer.put(frame)

    def _right_capture(self):
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
        left_frame = None
        right_frame = None
        while True:
            # read frames if they are ready
            #if not self._left_buffer.empty() and self._right_buffer.empty():
            if self._left_cam.frame_ready and self._right_cam.frame_ready:
                #left_frame = self._left_buffer.get()
                #right_frame = self._right_buffer.get()
                left_frame = self._left_cam.frame
                right_frame = self._right_cam.frame

                # rotate
                if self._rotation is not None:
                    left_frame = cv2.rotate(left_frame, self._rotation)
                    right_frame = cv2.rotate(right_frame, self._rotation)

                # build rendered frame
                self._frame = np.hstack(tuple([right_frame, left_frame]))
                #self._frame_buffer.put(self._frame)

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
    crop_area = (0,1080,480,1440)
    resolution = (1920, 1080)
    cam_left = Camera(path="/dev/shm/cam_left", resolution=resolution, crop_area=crop_area)
    cam_right = Camera(path="/dev/shm/cam_right", resolution=resolution, crop_area=crop_area)
    cameras = [cam_left, cam_right]

    # create capture session
    # There is no need to start cameras one by one because when object is created, capture is automatically started
    capture = Capture(cameras=cameras)
    capture.start()

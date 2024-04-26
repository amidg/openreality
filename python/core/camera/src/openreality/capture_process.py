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
from camera import Camera

ROTATION_TYPES = Literal[
    cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180,
    cv2.ROTATE_90_COUNTERCLOCKWISE
]

"""
   Capture class that combines camera stream from N cameras into one buffer 
"""
class Capture():
#class Capture(multiprocessing.Process):
    def __init__(self):
        #super().__init__()
        self._cam_list: List[Camera] = []
        self._rotation = None
        self._memory = "camera"
        
        # time
        self._ctime = 0
        self._ptime = 0
        self._fps = 0

    def run(self, cameras: List[Camera], rotation: ROTATION_TYPES = None):
        # do some setup
        if rotation is not None:
            try:
                assert rotation in get_args(ROTATION_TYPES)
                self._rotation = rotation
            except AssertionError:
                # TODO: add logger handler
                print(f"Incorrect rotation requested {rotation}: must be cv2.ROTATE_XX_YY type")

        # start cameras
        self._cam_list = cameras
        for cam in self._cam_list:
            cam.start()

        # wait for all cams to start
        cam_left = self._cam_list[0]
        cam_right = self._cam_list[1]
        while not (cam_left.frame_ok and cam_right.frame_ok):
            pass

        # create render buffer from two front cameras
        frame_left: np.ndarray = cam_left.frame
        frame_right: np.ndarray = cam_right.frame
        render_shared_memory = shared_memory.SharedMemory(
            create=True,
            size=(frame_left.nbytes+frame_right.nbytes),
            name=self._memory
        )
        render_shape = tuple([frame_right.shape[0] + frame_left.shape[0], frame_left.shape[1], frame_left.shape[2]])
        if self._rotation in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]:
            render_shape = tuple([frame_right.shape[1] + frame_left.shape[1], frame_left.shape[0], frame_left.shape[2]])
        render_frame_buffer = np.ndarray(
            render_shape,
            dtype=np.uint8,
            buffer=render_shared_memory.buf
        )

        # stream video to renderer
        while True:
            # iterate over all cameras
            for index, camera in enumerate(self._cam_list):
                # left eye
                if index == 0:
                    frame_left = camera.frame
                    if self._rotation is not None:
                        frame_left = cv2.rotate(frame_left, self._rotation)
                # right eye
                elif index == 1:
                    frame_right = camera.frame
                    if self._rotation is not None:
                        frame_right = cv2.rotate(frame_right, self._rotation)

            # build rendered frame
            rendered_frame = np.vstack(tuple([frame_right, frame_left]))
            #self._data_buffer.put(rendered_frame)
            np.copyto(render_frame_buffer, rendered_frame)

            # calculate fps
            self._ctime = time.time()
            self._fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime

        render_shared_memory.close()
        render_shared_memory.unlink()

        
# demo code to run this separately
if __name__ == "__main__":
    # start create list of cameras
    crop_area = (0,720,320,960)
    resolution = (1280,720)
    cam_left = Camera(device=2, resolution=resolution, crop_area=crop_area)
    cam_right = Camera(device=0, resolution=resolution, crop_area=crop_area)
    cameras = [cam_left, cam_right]

    # create capture session
    # There is no need to start cameras one by one because when object is created, capture is automatically started
    capture = Capture()
    capture_session = multiprocessing.Process(target=capture.run, args=(cameras, cv2.ROTATE_90_CLOCKWISE,))
    capture_session.start()

import argparse
import cv2
import numpy as np
import os
from time import time

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

from typing import Literal, List, get_args

ROTATION_TYPES = Literal[
    cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180,
    cv2.ROTATE_90_COUNTERCLOCKWISE
]

"""
    Sample camera class.
    It allows to start camera with specified resolution and FPS
"""
class Camera():
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        width: int = 1920,
        height: int = 1080,
        fps: float = 30,
    ):
        # camera parameters
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps

        # OpenCV capture parameters
        self._cap = cv2.VideoCapture(self._device)
        self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._cap.set(cv2.CAP_PROP_FPS, self._fps)

    @property
    def cap(self):
        return self._cap

    @property
    def width(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    @property
    def height(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

"""
   Capture class that combines camera stream from N cameras into one buffer 
"""
class Capture(multiprocessing.Process):
    def __init__(
        self,
        cameras: List[Camera],
        rotation: ROTATION_TYPES = None
    ):
        super().__init__()
        self._cam_list = cameras
        self._rotation = None
        self._memory = "camera"
        if rotation is not None:
            try:
                assert rotation in get_args(ROTATION_TYPES)
                self._rotation = rotation
            except AssertionError:
                # TODO: add logger handler
                print(f"Incorrect rotation requested {rotation}: must be cv2.ROTATE_XX_YY type")

    def run(self):
        # check if all cameras are ready
        cam_ready = True
        for cam in self._cam_list:
            cam_ready = cam_ready and cam.cap.isOpened()
    
        # if not ready, we quit
        # TODO: RaiseError
        if not cam_ready:
            exit()

        # if cameras are ready, we need to calculate the size of the buffer
        # TODO: add handler for the not same size of the frame
        all_cam_frames: List[np.ndarray] = []
        for cam in self._cam_list:
            if cam.cap.grab():
                #TODO: Handler of the errors here
                ret, frame = cam.cap.retrieve(0)

            # Flip frame if necessary
            if self._rotation is not None:
                frame = cv2.rotate(frame, self._rotation)

            # start creating stack of images
            all_cam_frames.append(frame)
        test_buf_frame = np.vstack(tuple(frame for frame in all_cam_frames))
        shm = shared_memory.SharedMemory(
            create=True, size=test_buf_frame.nbytes, name=self._memory
        )
        frame_buffer = np.ndarray(
            test_buf_frame.shape,
            dtype=test_buf_frame.dtype,
            buffer=shm.buf
        )

        # stream video
        # TODO: add handler when closed
        cam_frames: List[np.ndarray] = []
        while cam_ready:
            # get all frames
            for camera in self._cam_list:
                if camera.cap.grab():
                    ret, frame = cam.cap.retrieve(0)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Flip frame if necessary
                    if self._rotation is not None:
                        frame = cv2.rotate(frame, self._rotation)
                    cam_frames.append(frame)
                else:
                    cam_ready = False
                    break
    
            # build buffer
            buffer = np.vstack(tuple(frame for frame in cam_frames))
            np.copyto(frame_buffer, buffer)  # Copy frame to shared memory
            cam_frames = []

        # stop opencv stream
        for cam in self._cam_list:
            cam.cap.release()
        shm.close()
        shm.unlink()

        
# demo code to run this separately
if __name__ == "__main__":
    # start create list of cameras
    cam_left = Camera(device=0)
    cam_right = Camera(device=2)
    cameras = [cam_left, cam_right]

    # create capture session
    capture_session = Capture(cameras=cameras, rotation=cv2.ROTATE_90_CLOCKWISE)
    capture_session.start()

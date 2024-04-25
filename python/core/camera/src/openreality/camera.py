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
        fps: float = 30,
        rotation: ROTATION_TYPES = None
    ):
        super().__init__()

        # camera parameters
        self._device = device
        self._resolution = resolution
        self._fps = fps
        self._rotation = rotation

        # OpenCV capture parameters
        """
        DISPLAY=:0 gst-launch-1.0 v4l2src device=/dev/video0 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegparse ! jpegdec ! xvimagesink
        """
        self._gst_cmd = (
            f"gst-launch-1.0 v4l2src device=/dev/video{self._device} ! "
            f"image/jpeg,width={self._resolution[0]},height={self._resolution[1]},framerate={self._fps}/1 ! "
            f" jpegparse ! jpegdec ! "
            f"videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
        )
        self._cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)

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
    def cap(self):
        return self._cap

    @property
    def fps(self):
        return self._actual_fps

    def run(self):
        # get shared memory object
        shm = shared_memory.SharedMemory(create=True, size=self._frame_size, name=self._memory)
        buffer = np.ndarray(self._frame_shape, dtype=np.uint8, buffer=shm.buf)

        # run capture into the buffer
        while self._cap.isOpened():
            # read frames
            ret, frame = self._cap.read()
            if ret:
                # put frame to the buffer
                np.copyto(buffer, frame)

                # calculate fps
                self._ctime = time.time()
                self._actual_fps = 1/(self._ctime-self._ptime)
                self._ptime = self._ctime
                print(self._actual_fps)
        # capture fail
        self._cap.release()


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
        # time
        self._ctime = 0
        self._ptime = 0
        self._fps = 0

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

        # debug
        #cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # stream video
        # TODO: add handler when closed
        cam_frames: List[np.ndarray] = []
        while cam_ready:
            # get all frames
            for camera in self._cam_list:
                if camera.cap.grab():
                    ret, frame = camera.cap.retrieve(0)
                    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Flip frame if necessary
                    if self._rotation is not None:
                        frame = cv2.rotate(frame, self._rotation)
                    cam_frames.append(frame)
                else:
                    cam_ready = False
                    break
    
            # build buffer
            buffer = np.vstack(tuple(frame for frame in reversed(cam_frames)))
            np.copyto(frame_buffer, buffer)  # Copy frame to shared memory
            cam_frames = []

            # debug
            #print(buffer.shape)
            #cv2.imshow("render", buffer)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

            # calculate fps
            self._ctime = time.time()
            self._fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime
            print(self._fps)

        # stop opencv stream
        for cam in self._cam_list:
            cam.cap.release()
        shm.close()
        shm.unlink()

        
# demo code to run this separately
if __name__ == "__main__":
    # start create list of cameras
    #cam_left = Camera(device=3)
    #cam_right = Camera(device=0)
    #cameras = [cam_left, cam_right]

    ## create capture session
    #capture_session = Capture(cameras=cameras, rotation=cv2.ROTATE_90_CLOCKWISE)
    #capture_session.start()

    # test cam
    cam_left = Camera(device=0, resolution=(1920, 1080))
    cam_left.start()

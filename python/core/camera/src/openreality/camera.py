import cv2
import numpy as np
import time
from typing import Literal, List, Tuple, get_args

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

"""
    Sample camera class.
    It allows to start camera with specified resolution and FPS
"""
class Camera():
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        resolution: Tuple[int, int],
        fps: float = 30,
        name: str = "camera"
    ):
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
        self._cap = cv2.VideoCapture(self._gst_cmd, cv2.CAP_GSTREAMER)

        # performance metrics
        self._ctime = 0
        self._ptime = 0
        self._actual_fps = 0

        # data
        self._memory = name
        self._frame_shape = (self._resolution[1], self._resolution[0], 3)
        self._frame_size = np.full(self._frame_shape, np.uint8).nbytes

    @property
    def device(self):
        return self._device

    @property
    def ready(self):
        return self._cap.isOpened()

    @property
    def resolution(self):
        return self._resolution

    @property
    def fps(self):
        return self._actual_fps

    @property
    def gst(self):
        return self._gst_cmd

    @property
    def name(self):
        return self._memory

    @property
    def frame_shape(self):
        return self._frame_shape

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def cap(self):
        return self._cap

    def run(self):
        # get shared memory object
        shm = shared_memory.SharedMemory(create=True, size=self._frame_size, name=self._memory)
        buffer = np.ndarray(self._frame_shape, dtype=np.uint8, buffer=shm.buf)

        # run capture into the buffer
        if not self._cap.isOpened():
            print("Failed to open capture")
            # TODO: RaiseError
            exit()

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
        shm.close()
        shm.unlink()
        
# demo code to run this separately
if __name__ == "__main__":
    # test cam
    cam_left = Camera(device=0, resolution=(1280, 720), name="left_eye")
    cam_left.run()

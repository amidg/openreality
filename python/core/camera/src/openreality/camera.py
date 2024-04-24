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
    Camera based on FFMPEG
"""
class CameraFFMPEG(multiprocessing.Process):
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        resolution: Tuple[int, int], # width, height 
        fps: int = 30
    ):
        super().__init__()
        self._device = device
        self._resolution = resolution
        self._fps = fps
        self._capture_pipeline = self._ffmpeg()
        self._frame_shape = (self._resolution[1], self._resolution[0], 3)
        self._frame_size = np.prod(self._frame_shape)

        # performance metrics
        self._ctime = 0
        self._ptime = 0
        self._actual_fps = 0

        # data
        self._memory = f"camera{self._device}"

    @property
    def device(self):
        return self._device

    @property
    def resolution(self):
        return self._resolution

    @property
    def fps(self):
        return self._actual_fps

    @property
    def frame_shape(self) -> Tuple[int, int, int]:
        # height, width, color depth in bytes
        return self._frame_shape 

    def _ffmpeg(self):
        command = [
            f"ffmpeg -f v4l2",
            f"-r {self._fps}",
            f"-video_size {self._resolution[0]}x{self._resolution[1]}",
            f"-input_format mjpeg",
            f"-i /dev/video{self._device}",
            f"-vcodec mjpeg",  # Input codec set to mjpeg
            f"-an -vcodec rawvideo",  # Decode the MJPEG stream to raw video
            f"-pix_fmt bgr24",
            f"-vsync 2",
            f"-f image2pipe -"
        ]

        return subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8
        )

    def _wait_for_cam(self):
        for _ in range(30):
            frame = self._read()
            if frame is not None:
                return True
        return False

    def _read(self):
        raw_image = self._capture_pipeline.stdout.read(self._frame_size)
        if len(raw_image) != self._frame_size:
            return None
        return np.frombuffer(raw_image, dtype=np.uint8).reshape(self._frame_shape)

    def run(self):
        if not self._wait_for_cam():
            # TODO: RaiseError
            exit()

        # shared memory
        shm = shared_memory.SharedMemory(create=True, size=self._frame_size.nbytes, name=self._memory)
        buffer = np.ndarray(self._frame_shape, dtype=np.uint8, buffer=shm.buf)

        # TODO: How do I check if it failed?
        while True:
            # get frame
            frame = self._read()
            np.copyto(buffer, frame)

            # calculate fps
            self._ctime = time.time()
            self._actual_fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime
            print(self._actual_fps)
        # release pipeline
        self._capture_pipeline.terminate()


"""
    Sample camera class.
    It allows to start camera with specified resolution and FPS
"""
class Camera(multiprocessing.Process):
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        width: int = 1920,
        height: int = 1080,
        fps: float = 30,
        rotation: ROTATION_TYPES = None
    ):
        super().__init__()

        # camera parameters
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        self._rotation = rotation

        # OpenCV capture parameters
        self._cap = cv2.VideoCapture(self._device)
        self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._cap.set(cv2.CAP_PROP_FPS, self._fps)

        # performance metrics
        self._ctime = 0
        self._ptime = 0
        self._actual_fps = 0

        # data
        self._buffer = queue.SimpleQueue()
        self._memory = f"camera{self._device}"

    @property
    def device(self):
        return self._device

    @property
    def cap(self):
        return self._cap

    @property
    def width(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    @property
    def height(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    @property
    def fps(self):
        return self._actual_fps

    @property
    def frame_shape(self) -> Tuple[int, int, int]:
        # width, height, color depth in bytes
        return (self._width, self._height, 3)

    @property
    def buffer(self):
        return self._buffer

    def run(self):
        # get info about frame dimensions
        if self._cap.isOpened():
            ret, frame = self._cap.read()
            if not ret:
                exit()

        shm = shared_memory.SharedMemory(create=True, size=frame.nbytes, name=self._memory)
        buffer = np.ndarray(frame.shape, dtype=frame.dtype, buffer=shm.buf)

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
    cam_left = CameraFFMPEG(device=2, resolution=(1920, 1080))
    cam_left.start()

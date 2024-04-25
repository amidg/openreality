import cv2
import numpy as np
import time
from typing import Literal, List, Dict, Tuple, Union, get_args

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

# openreality
from camera import Camera

ROTATION_TYPES = Literal[
    cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180,
    cv2.ROTATE_90_COUNTERCLOCKWISE
]

"""
Dual camera capture via gstreamer but slow
DISPLAY=:0 gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_0 \
mqueue.src_2 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_1 \
videomixer name=videomux sink_1::ypos=1280 ! video/x-raw,width=720,height=2560 ! queue ! xvimagesink sync=false
"""

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
        # create output device
        cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # check if all cameras are ready
        cam_ready = True
        for camera in self._cam_list:
            cam_ready = cam_ready and camera.ready
    
        # if not ready, we quit
        # TODO: RaiseError
        if not cam_ready:
            exit()

        # create render buffer from two front cameras
        frame_left = self._cam_list[0].frame
        frame_right = self._cam_list[1].frame
        if self._rotation is not None:
            frame_left = cv2.rotate(frame_left, self._rotation)
            frame_right = cv2.rotate(frame_right, self._rotation)
        render_shared_memory = shared_memory.SharedMemory(
            create=True,
            size=(frame_left.size+frame_right.size),
            name=self._memory
        )
        render_frame_buffer = np.ndarray(
            tuple([frame_right.shape[0] + frame_left.shape[0], frame_left.shape[1], frame_left.shape[2]]),
            dtype=np.uint8,
            buffer=render_shared_memory.buf
        )

        # stream video to renderer
        cam_ok = True
        while cam_ok:
            # iterate over all cameras
            for index, camera in enumerate(self._cam_list):
                if camera.cap.grab():
                    # left eye
                    if index == 0:
                        ret, frame_left = camera.cap.retrieve(0)
                        if not ret:
                            cam_ok = False
                            break
                        if self._rotation is not None:
                            frame_left = cv2.rotate(frame_left, self._rotation)
                    # right eye
                    elif index == 1:
                        ret, frame_right = camera.cap.retrieve(0)
                        if not ret:
                            cam_ok = False
                            break
                        if self._rotation is not None:
                            frame_left = cv2.rotate(frame_right, self._rotation)
                else:
                    cam_ok = False

            # build rendered frame
            rendered_frame = np.vstack(tuple([frame_right, frame_left]))
            np.copyto(render_frame_buffer, rendered_frame)

            # calculate fps
            self._ctime = time.time()
            self._fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime
            print(self._fps)

            # show frame
            cv2.imshow("render", rendered_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # stop opencv stream
        for camera in self._cam_list:
            camera.cap.release()
        render_shared_memory.close()
        render_shared_memory.unlink()

        
# demo code to run this separately
if __name__ == "__main__":
    # start create list of cameras
    cam_left = Camera(device=2, resolution=(1280,720), name="left_eye")
    cam_right = Camera(device=0, resolution=(1280,720), name="right_eye")
    cameras = [cam_left, cam_right]

    # create capture session
    # There is no need to start cameras one by one because when object is created, capture is automatically started
    capture_session = Capture(cameras=cameras, rotation=cv2.ROTATE_90_CLOCKWISE)
    capture_session.start()

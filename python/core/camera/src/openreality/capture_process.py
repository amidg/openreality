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

        # start all cams
        #self._camera_ps: List[multiprocessing.Process] = []
        #for camera in self._cam_list:
        #    # TODO: add logger handler
        #    self._camera_ps.append(multiprocessing.Process(target=camera.run))
        #for camera in self._camera_ps:
        #    camera.start()

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

        # if cameras are ready, we need to calculate the size of the shared memory buffer
        cam_memory: Dict[str, shared_memory.SharedMemory] = {}
        cam_frames: Dict[str, np.ndarray] = {}
        cam_frames_size: Dict[str, np.nbytes] = {}
        for camera in self._cam_list:
            # TODO: add handler for the not same size of the frame
            cam_memory[camera.name] = shared_memory.SharedMemory(name=camera.name)
            cam_frames[camera.name] = np.ndarray(
                camera.frame_shape,
                dtype=np.uint8,
                buffer=cam_memory[camera.name].buf
            )
            cam_frames_size[camera.name] = np.full(camera.frame_shape, np.uint8).nbytes

        # create render buffer for two main camera
        left_cam_name = "left_eye"
        right_cam_name = "right_eye"
        frame_left = cam_frames[left_cam_name]
        frame_right = cam_frames[right_cam_name]
        if self._rotation is not None:
            frame_left = cv2.rotate(frame_left, self._rotation)
            frame_right = cv2.rotate(frame_right, self._rotation)
        render_shared_memory = shared_memory.SharedMemory(
            create=True,
            size=(cam_frames_size[left_cam_name]+cam_frames_size[right_cam_name]),
            name=self._memory
        )
        render_frame_buffer = np.ndarray(
            tuple([frame_right.shape[0] + frame_left.shape[0], frame_left.shape[1], frame_left.shape[2]]),
            dtype=np.uint8,
            buffer=render_shared_memory.buf
        )

        # stream video to renderer
        while True:
            # get frames
            frame_left = cam_frames[left_cam_name]
            frame_right = cam_frames[right_cam_name]

            # apply rotation
            if self._rotation is not None:
                frame_left = cv2.rotate(frame_left, self._rotation)
                frame_right = cv2.rotate(frame_right, self._rotation)

            # send those frames to the buffer
            #rendered_frame = cv2.vconcat([frame_right, frame_left])
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

        # stop all cameras
        for camera in self._camera_ps:
            camera.stop()
            camera.join()

        
# demo code to run this separately
if __name__ == "__main__":
    # start create list of cameras
    cam_left = Camera(device=2, resolution=(1280,720), name="left_eye")
    cam_right = Camera(device=0, resolution=(1280,720), name="right_eye")
    cameras = [cam_left, cam_right]

    # start all cams
    camera_ps: List[multiprocessing.Process] = []
    for camera in cameras:
        # TODO: add logger handler
        camera_ps.append(multiprocessing.Process(target=camera.run))
    for camera in camera_ps:
        camera.start()

    # create capture session
    capture_session = Capture(cameras=cameras, rotation=cv2.ROTATE_90_CLOCKWISE)
    capture_session.start()

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

# capture
from openreality.sensors.cameras.imx219 import imx219
from openreality.sensors.stereo_camera import StereoCamera

camera_mode = imx219[1].parameters # width, height, fps
crop_area = (
    # (204,1644,992,2272) # y0,y1,x0,x1 @ 1440p
    int((camera_mode[1] - 1440)/2), # y0, top
    int(camera_mode[1] - (camera_mode[1] - 1440)/2), # y1, bottom
    int((camera_mode[0] - 1280)/2), # x0, left
    int(camera_mode[0] - (camera_mode[0] - 1280)/2), # x1, right
)
stereo_camera = StereoCamera(
    device_left=0,
    device_right=1,
    resolution=(camera_mode[0], camera_mode[1]),
    crop_area=crop_area,
    fps=camera_mode[2]
)

# buffer
from openreality.sdk.framebuffer import RingBuffer
buffer = RingBuffer(memmap = "/dev/shm/camera")
fps = 0

def read_camera():
    while stereo_camera.opened:
        if stereo_camera.frame_ready:
            buffer.add(stereo_camera.frame)

def read_framebuffer():
    ctime = 0
    ptime = 0
    global fps
    while True:
        # read buffer
        frame = buffer.last_frame

        # calculate fps
        ctime = time.time()
        fps = 1/(ctime-ptime)
        ptime = ctime


# camera thread
cam_thread = threading.Thread(target=read_camera)
cam_thread.start()
framebuffer_thread = threading.Thread(target=read_framebuffer)
framebuffer_thread.start()

# check for 180 frames ~ 1 min
for i in range(180):
    print(f"Frame {i}: Cam FPS {stereo_camera.fps} VS buffer fps {fps}")

# when all threads end
cam_thread.stop()
cam_thread.join()
framebuffer_thread.stop()
framebuffer_thread.join()
stereo_camera.cap.release()

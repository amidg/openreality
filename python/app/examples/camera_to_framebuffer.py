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
ring_buffer = RingBuffer(memmap = "/dev/shm/camera")

while True:
    # vars
    ctime = 0
    ptime = 0

    # check for 900 frames ~ 30 seconds
    frame = 0
    while stereo_camera.opened:
        # read camera
        if stereo_camera.frame_ready:
            ring_buffer.add(stereo_camera.frame)
            frame = frame + 1
            print(f"Frame {frame}: Cam FPS {stereo_camera.fps}")
        if frame == 900:
            break
    break
stereo_camera.cap.release()

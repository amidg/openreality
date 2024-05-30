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

stereo_camera = StereoCamera(
    device_left=0,
    device_right=1,
    config=imx219[1].parameters, # Tuple(width, height, fps)
    target_resolution=(2560,1440),
    rotation=2
)

# buffer
from openreality.sdk.framebuffer import FrameBuffer
ring_buffer = FrameBuffer(memmap = "/dev/shm/camera")

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

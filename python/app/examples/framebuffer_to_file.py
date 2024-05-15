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

# buffer
from openreality.sdk.framebuffer import RingBuffer
ring_buffer = RingBuffer(memmap = "/dev/shm/camera")

# time
fps = 0
ctime = 0
ptime = 0
img = None

# check for 900 frames ~ 30 seconds
for i in range(900):
    img = ring_buffer.last_frame

    # read camera from buffer
    if img.size > 0:
        # calculate fps
        ctime = time.time()
        fps = 1/(ctime-ptime)
        ptime = ctime
        print(f"Frame {i}: buffer fps {fps}")

# save last frame
cv2.imwrite("/home/dmitrii/Pictures/buffer.png", img)

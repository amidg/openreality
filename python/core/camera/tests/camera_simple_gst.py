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

gst_cmd = (
    f"gst-launch-1.0 v4l2src device=/dev/video0 ! "
    f"image/jpeg,width=1920,height=1080,framerate=30/1 ! "
    f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
)

print(gst_cmd)
cap = cv2.VideoCapture(gst_cmd, cv2.CAP_GSTREAMER)

# performance metrics
ctime = 0
ptime = 0
actual_fps = 0

# data
memory = f"camera"
frame_shape = (1080, 1920, 3)
frame_size = np.full(frame_shape, np.uint8).nbytes

# get shared memory object
shm = shared_memory.SharedMemory(create=True, size=frame_size, name=memory)
buffer = np.ndarray(frame_shape, dtype=np.uint8, buffer=shm.buf)

# debug window
cv2.namedWindow("render", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# run capture into the buffer
if not cap.isOpened():
    print("Failed to open capture")
    exit()

while cap.isOpened():
    # read frames
    ret, frame = cap.read()
    if ret:
        # put frame to the buffer
        np.copyto(buffer, frame)

        # calculate fps
        ctime = time.time()
        actual_fps = 1/(ctime-ptime)
        ptime = ctime
        print(actual_fps)

        # debug
        cv2.imshow("render", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# capture end
cap.release()
shm.close()
shm.unlink()

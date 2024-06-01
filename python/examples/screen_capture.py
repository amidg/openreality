import cv2
import numpy
import time

# ring buffer
import openreality.sdk.framebuffer as fb
ring_buffer = fb.FrameBuffer(memmap="/dev/shm/camera")

# nvidia pipeline for encoding
video_out_pipeline = cv2.VideoWriter(
    # command
    f"appsrc ! video/x-raw, format=(string)BGR ! "
    f"videoconvert ! video/x-raw, format=(string)BGRx ! "
    f"nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12 ! "
    f"nvv4l2h265enc control-rate=0 "
    f"preset-level=2 maxperf-enable=true profile=1 ! "
    f"h265parse ! splitmuxsink location=~/Videos/test-%05d.mkv "
    f"max-size-bytes=2000000000 muxer=matroskamux -e"
    cv2.CAP_GSTREAMER,
    60, #fps,
    (self.width, self.height),
)

start_time = time.time()
while time.time() - start_time < 60:
    img = ring_buffer.last_frame

    if img.size > 0:
        video_out_pipeline.write(frame)
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

import cv2
import numpy as np
import subprocess as sp
import shlex
import time

width = 1280
height = 720

gst_cmd = (
    f"gst-launch-1.0 --quiet v4l2src device=/dev/video0 ! "
    f"image/jpeg,width={width},height={height},framerate={30}/1 ! "
    f"jpegdec ! videoconvert ! video/x-raw, format=RGB ! fdsink"
)

# too slow
#gst_cmd = (
#    f"gst-launch-1.0 multiqueue max-size-buffers=1 name=mqueue "
#    f"v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_1 "
#    f"v4l2src device=/dev/video2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_2 "
#    f"mqueue.src_1 ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_0 "
#    f"mqueue.src_2 ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_1 "
#    f"videomixer name=videomux sink_1::ypos=1280 ! video/x-raw,width=720,height=2560 ! fdsink sync=False"
#)

# https://stackoverflow.com/questions/29794053/streaming-mp4-video-file-on-gstreamer
p = sp.Popen(shlex.split(gst_cmd), stdout=sp.PIPE)

# performance metrics
ctime = 0
ptime = 0
actual_fps = 0

while True:
    raw_image = p.stdout.read(width * height * 3)

    if len(raw_image) < width*height*3:
        break

    image = np.frombuffer(raw_image, np.uint8).reshape((height, width, 3))
    cv2.imshow('image', image)

    # calculate fps
    ctime = time.time()
    actual_fps = 1/(ctime-ptime)
    ptime = ctime
    print(actual_fps)
    key = cv2.waitKey(1000)

p.stdout.close()
p.wait()
cv2.destroyAllWindows()

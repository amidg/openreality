DISPLAY=:0 gst-launch-1.0 tee name=stream v4l2src device=/dev/video0 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegparse ! jpegdec ! xvimagesink stream. v4l2src device=/dev/video2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegparse ! jpegdec ! xvimagesink stream.

DISPLAY=:0 gst-launch-1.0 v4l2src device=/dev/video0 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegparse ! jpegdec ! xvimagesink

DISPLAY=:0 gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! xvimagesink

DISPLAY=:0 gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! xvimagesink

DISPLAY=:0 gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! appsink drop=True

import cv2
gstreamer_str = "gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! videoconvert ! video/x-raw,format=BGR ! queue ! appsink drop=1"

cap = cv2.VideoCapture(gstreamer_str, cv2.CAP_GSTREAMER)
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Input via Gstreamer", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        else:
            break
cap.release()
cv2.destroyAllWindows()

gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! jpegdec ! videoconvert ! autovideosink \
mqueue.src_2 ! jpegdec ! videoconvert ! autovideosink

 
mqueue.src_1 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! rotate angle=1.57 ! queue ! videomux.sink_0 \
mqueue.src_2 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! rotate angle=1.57 ! queue ! videomux.sink_1 \

mqueue.src_1 ! jpegdec ! videoconvert ! queue ! videomux.sink_0 \
mqueue.src_2 ! jpegdec ! videoconvert ! queue ! videomux.sink_1 \
 
DISPLAY=:0 gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_0 \
mqueue.src_2 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_1 \
videomixer name=videomux sink_1::ypos=1280 ! video/x-raw,width=720,height=2560 ! queue ! xvimagesink sync=false


gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! shmsink socket-path=/tmp/cam1 sync=true wait-for-connection=false shm-size=10000000

WORKING!
DISPLAY=:0 gst-launch-1.0 shmsrc socket-path=/tmp/cam1 ! image/jpeg,width=1280,height=720,framerate=30/1 ! jpegdec ! queue ! videoconvert ! xvimagesink sync=FalseA

Dual camera shm
gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! shmsink socket-path=/tmp/cam1 sync=true wait-for-connection=false shm-size=10000000 \
mqueue.src_2 ! shmsink socket-path=/tmp/cam2 sync=true wait-for-connection=false shm-size=10000000

gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! shmsink socket-path=/tmp/cam1 sync=true wait-for-connection=false shm-size=10000000 \
mqueue.src_2 ! shmsink socket-path=/tmp/cam2 sync=true wait-for-connection=false shm-size=10000000

gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_0 \
mqueue.src_2 ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_1 \
videomixer name=videomux sink_1::ypos=1280 ! video/x-raw,width=720,height=2560 ! fdsink



DISPLAY=:0 gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_1 \
v4l2src device=/dev/video2 ! image/jpeg,width=1280,height=720,framerate=30/1 ! mqueue.sink_2 \
mqueue.src_1 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_0 \
mqueue.src_2 ! jpegdec ! videoconvert ! video/x-raw, format=RGB ! videoflip method=clockwise ! queue ! videomux.sink_1 \
videomixer name=videomux sink_1::ypos=1280 ! video/x-raw,width=720,height=2560 ! queue ! xvimagesink sync=false

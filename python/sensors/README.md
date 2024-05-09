### Nvidia based camera sync and output
Basic streaming to the screen
```
gst-launch-1.0 nvarguscamerasrc sensor-id=0 silent=false ! "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1" ! nvvidconv flip-method=2 ! "video/x-raw,width=1920,height=1080"  ! nveglglessink sync=false
```

Dual camera to two frames side by side:
```
gst-launch-1.0 nvcompositor name=comp \
sink_0::xpos=0 sink_0::ypos=0 sink_0::width=1920 sink_0::height=1080 \
sink_1::xpos=1920 sink_1::ypos=0 sink_1::width=1920 sink_1::height=1080 ! \
'video/x-raw(memory:NVMM),format=RGBA' ! nv3dsink \
nvarguscamerasrc sensor_id=0 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv flip-method=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, format=RGBA' ! comp.sink_0 \
nvarguscamerasrc sensor_id=1 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv flip-method=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, format=RGBA' ! comp.sink_1
```

Dual camera to video:
```
gst-launch-1.0 \
nvarguscamerasrc sensor_id=0 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv flip-method=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, format=RGBA' ! comp.sink_0 \
nvarguscamerasrc sensor_id=1 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv flip-method=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, format=RGBA' ! comp.sink_1 \
nvcompositor name=comp \
sink_0::xpos=0 sink_0::ypos=0 sink_0::width=1920 sink_0::height=1080 \
sink_1::xpos=1920 sink_1::ypos=0 sink_1::width=1920 sink_1::height=1080 ! \
'video/x-raw(memory:NVMM),format=RGBA' ! nvvidconv ! 'video/x-raw(memory:NVMM),format=(string)NV12' ! nvv4l2h265enc control-rate=0 preset-level=2 maxperf-enable=true profile=1 ! h265parse ! splitmuxsink location=capture-%05d.mkv max-size-bytes=2000000000 muxer=matroskamux -e
```

Dual camera to appsink:
```
 
```

Sample SHMSink write and SHMSrc read:
`/dev/shm` is used because it resides in RAM via tmpfs ramdisk (allowed since kernel 2.6) while /tmp is on the storage itself.
```
gst-launch-1.0 videotestsrc ! x264enc ! shmsink socket-path=/dev/shm/foo sync=true wait-for-connection=false shm-size=10000000
gst-launch-1.0 shmsrc socket-path=/dev/shm/foo ! h264parse ! avdec_h264 ! videoconvert ! ximagesink
```

SHMSink and SHMSrc using real camera and nvarguscamerasrc:
Raw Video:
```
gst-launch-1.0 nvarguscamerasrc sensor-id=0 silent=false ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1' ! nvvidconv ! 'video/x-raw,width=1920,height=1080,format=BGRx' ! videoconvert ! 'video/x-raw,width=1920,height=1080,format=BGR' ! shmsink socket-path=/dev/shm/foo sync=false wait-for-connection=false shm-size=20000000

gst-launch-1.0 nvarguscamerasrc sensor-id=0 silent=false ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1' ! nvvidconv ! 'video/x-raw,width=1920,height=1080,format=RGBA' ! shmsink socket-path=/dev/shm/foo sync=false wait-for-connection=false shm-size=20000000

gst-launch-1.0 shmsrc socket-path=/dev/shm/foo ! 'video/x-raw,width=1920,height=1080,format=RGBA' ! nvoverlaysink
```


Scan for windows:
```
wmctrl -lp
```

Get window ID and pass it to the gst:
```
gst-launch-1.0 ximagesrc xid=0x03200002 ! videoconvert ! x264enc ! shmsink socket-path=/dev/shm/foo sync=true wait-for-connection=false shm-size=10000000

gst-launch-1.0 shmsrc socket-path=/dev/shm/foo ! h264parse ! avdec_h264 ! videoconvert ! ximagesink
```


```
gst-launch-1.0 nvcompositor name=comp \
sink_0::xpos=0 sink_0::ypos=0 sink_0::width=1920 sink_0::height=1080 \
sink_1::xpos=1920 sink_1::ypos=0 sink_1::width=1920 sink_1::height=1080 ! \
'video/x-raw(memory:NVMM),format=RGBA' ! nvvidconv ! 'video/x-raw(memory:NVMM),format=(string)NV12' ! nvv4l2h265enc control-rate=0 preset-level=2 maxperf-enable=true profile=1 ! h265parse ! splitmuxsink location=capture-%05d.mkv max-size-bytes=2000000000 muxer=matroskamux -e \
nvarguscamerasrc sensor_id=0 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv flip-method=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, format=RGBA' ! comp.sink_0 \
nvarguscamerasrc sensor_id=1 ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1' ! nvvidconv flip-method=0 ! 'video/x-raw(memory:NVMM),width=1920, height=1080, format=RGBA' ! comp.sink_1
```





Dual Camera with sync:
```
gst-launch-1.0 \
multiqueue max-size-buffers=1 name=mqueue \
nvarguscamerasrc sensor-id=0 silent=false ! “video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1” ! mqueue.sink_1 \
nvarguscamerasrc sensor-id=1 silent=false ! “video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1” ! mqueue.sink_2 \
mqueue.src_1 ! nvvidconv flip-method=2 ! "video/x-raw,width=1920,height=1080" ! queue ! videomux.sink_0 \
mqueue.src_2 ! nvvidconv flip-method=2 ! "video/x-raw,width=1920,height=1080" ! queue ! videomux.sink_1 \
videomixer name=videomux sink_1::ypos=1920 ! video/x-raw,width=1080,height=3840 ! nveglglessink sync=false
```

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

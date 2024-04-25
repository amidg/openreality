import cv2

## Update
gst = (
    f"gst-launch-1.0 shmsrc socket-path=/tmp/cam1 ! "
    f"image/jpeg,width=1280,height=720,framerate=30/1 ! "
    f"jpegdec ! videoconvert ! queue ! appsink drop=True sync=False"
)
cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Cannot capture from camera. Exiting.")
    quit()


while True:
    ret, frame = cap.read()
    #
    if ret == False:
        break

    cv2.imshow("FrameREAD",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

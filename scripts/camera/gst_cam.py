import cv2
#gstreamer_str = "gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! appsink drop=1"
gstreamer_str = "v4l2src device=/dev/video0 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! appsink drop=1"

cap = cv2.VideoCapture(gstreamer_str, cv2.CAP_GSTREAMER)
print(f"Capture open: {cap.isOpened()}")
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Input via Gstreamer", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    #else:
    #    break
cap.release()
cv2.destroyAllWindows()

import cv2
import numpy as np

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

class DemoCamera(multiprocessing.Process):
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        width: int = 1920,
        height: int = 1080,
        fps: float = 30,
    ):
        super().__init__()
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        
    def run(self):
        # create capture device
        cap = cv2.VideoCapture(self._device)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap.set(cv2.CAP_PROP_FPS, self._fps)

        # check if device is opened
        # TODO: add proper error checking
        if cap.isOpened() is not True:
            print("Cannot open camera. Exiting.")
            quit()

        # stream image
        while True:
            # Get the frame
            ret, frame = cap.read()
            # Check
            if ret is True:
                cv2.imshow(f"Camera {self._device}", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # TODO: logging handler
                print("camera capture failed")
        # stop opencv stream
        cap.release()

        
# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam_left = DemoCamera(device=0)
    test_cam_left.start()
    #test_cam_right = DemoCamera(device=1)
    #test_cam_right.start()

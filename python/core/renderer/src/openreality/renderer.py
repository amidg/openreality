import cv2
import numpy as np

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

"""
    Renderer program that takes image stream and creates renderer instance
"""
class CameraStreamer(multiprocessing.Process):
    def __init__(
        self,
        device: int, # 1 for /dev/video1
        width: int = 1920,
        height: int = 1080,
        fps: float = 30
    ):
        super().__init__()
        self._device = device
        self._memory = f"/tmp/cam{device}"
        self._width = width
        self._height = height
        self._fps = fps

        # shared memory device
        # TODO: make frame and shm parameters programmatic, 3*8 is color depth 24bit
        self._gst = (
            f"shmsrc socket-path={self._memory} ! " \
            f"video/x-raw, format=BGR, width={self._width}, height={self._height}, pixel-aspect-ratio=1/1, framerate={self._fps}/1 ! "\
            f"decodebin ! videoconvert ! appsink"
        )
         

    def run(self):
        # create capture device
        cap = cv2.VideoCapture(self._gst, cv2.CAP_GSTREAMER)

        # TODO: add proper handling
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                cv2.imshow("Input via Gstreamer", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        cap.release()
        cv2.destroyAllWindows()


# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam = CameraStreamer(device=1)
    test_cam.start()

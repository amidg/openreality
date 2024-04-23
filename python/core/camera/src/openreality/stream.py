import cv2
import numpy as np

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

"""
    Demo Streamer class from the shared memory buffer.
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
        self._memory = f"cam{device}"
        self._width = width
        self._height = height
        self._fps = fps

        # shared memory device
        # TODO: make frame and shm parameters programmatic, 3*8 is color depth 24bit
        self._shm = shared_memory.SharedMemory(name=self._memory)
        self._frame = np.ndarray((self._height, self._width, 3), dtype=np.dtypes.UInt8DType, buffer=self._shm.buf)
         

    def run(self):
        try:
            while True:
                cv2.imshow(f"Camera Stream from {self._memory}", self._frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self._shm.close()


# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam = CameraStreamer(device=0)
    test_cam.start()

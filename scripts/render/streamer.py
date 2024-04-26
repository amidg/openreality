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
        memmap: str,
        width: int = 3840,
        height: int = 1080,
        fps: float = 30
    ):
        super().__init__()
        self._memory = memmap
        self._width = width
        self._height = height
        self._fps = fps

    def run(self):
        # shared memory device
        self._shm = shared_memory.SharedMemory(name=self._memory, create=False)
        self._frame = np.ndarray(
            (self._width, self._height, 3),
            dtype="uint8",
            buffer=self._shm.buf
        )

        # read shared memory device
        while True:
            cv2.imshow(f"Camera", self._frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # close shared memory
        self._shm.close()
        self._shm.unlink()

# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam = CameraStreamer(memmap="camera")
    test_cam.start()

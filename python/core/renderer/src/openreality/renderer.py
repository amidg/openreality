import cv2
import numpy as np

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

"""
    Renderer program that takes image stream and creates renderer instance
"""
class Renderer(multiprocessing.Process):
    def __init__(
        self,
        memmap: str = "camera",
        buf_width: int = 1280,
        buf_height: int = 480,
        buf_depth: int = 3
    ):
        super().__init__()
        self._memmap = memmap
        self._width = buf_width
        self._height = buf_height
        self._depth = buf_depth

    def run(self):
        # create output device
        cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # get shared memory
        self._shm = shared_memory.SharedMemory(name=self._memmap)
        self._frame = np.ndarray(
            (self._width, self._height, self._depth),
            dtype="uint8",
            buffer=self._shm.buf
        )

        # TODO: add proper handling
        while True:
            cv2.imshow("render", self._frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # close shared memory
        self._shm.close()
        self._shm.unlink()
        cv2.destroyAllWindows()


# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_render = Renderer(memmap="camera")
    test_render.start()

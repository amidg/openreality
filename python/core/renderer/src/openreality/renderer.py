import cv2
import numpy as np
import time
from typing import Tuple
import multiprocessing
from multiprocessing import shared_memory

"""
    Renderer program that takes image stream and creates renderer instance
"""
class Renderer(multiprocessing.Process):
    def __init__(
        self,
        memmap: str,
        resolution: Tuple[int, int]
    ):
        super().__init__()
        self._memmap = memmap
        self._resolution = resolution

        # performance metrics
        self._ctime = 0
        self._ptime = 0
        self._actual_fps = 0

        # data
        self._frame_shape = (self._resolution[1], self._resolution[0], 3)
        self._frame_size = np.full(self._frame_shape, np.uint8).nbytes

    def run(self):
        # create output device
        cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # get shared memory
        shm = shared_memory.SharedMemory(name=self._memmap)
        frame = np.ndarray(self._frame_shape, dtype="uint8", buffer=shm.buf)

        # TODO: add proper handling
        while True:
            cv2.imshow("render", frame)
            # calculate fps
            self._ctime = time.time()
            self._actual_fps = 1/(self._ctime-self._ptime)
            self._ptime = self._ctime
            print(self._actual_fps)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        # close shared memory
        shm.close()
        shm.unlink()
        cv2.destroyAllWindows()


# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_render = Renderer(memmap="camera", resolution=(720, 2560))
    test_render.start()

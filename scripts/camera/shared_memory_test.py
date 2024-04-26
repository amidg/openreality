import numpy as np

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

"""
    SharedMemory reader class
"""
class SharedMemoryReader(multiprocessing.Process):
    def __init__(self, device: int = 0):
        super().__init__()
        self._device = device
        self._memory = f"cam{device}"

    def run(self):
        # create shared memory object
        self._shm = shared_memory.SharedMemory(name=self._memory)
        self._frame = np.ndarray(
            (1920, 1080, 3),
            dtype="uint8",
            #dtype=np.dtypes.UInt8DType,
            buffer=self._shm.buf
        )

        # read shared memory
        while True:
            print(self._frame)
        self._shm.close()
        self._shm.unlink()

        
# demo code to run this separately
if __name__ == "__main__":
    # reader
    test_reader = SharedMemoryReader(device=0)
    test_reader.start()

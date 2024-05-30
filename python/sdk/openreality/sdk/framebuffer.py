import collections
import numpy as np
from typing import Tuple

"""
    This class creates the frame buffer in Python memory + memmap in numpy for other processes.
    add() adds frame to the ring buffer, however it won't be immediately available
    last_frame retrieves frame from the memory in RAM to be used in other process
"""
class FrameBuffer():
    def __init__(
        self,
        # ring buffer is assumed to have a shared memory storage
        memmap: str, # e.g. /dev/shm/capture
        buffer_size: int = 10,
        shape: Tuple[int, int, int] = (1440,2560,3), # arbitrary number
    ):
        self._buffer = collections.deque(maxlen=buffer_size)
        self._shape = shape
        self._last_frame = np.empty(self._shape, dtype=np.uint8)
        # TODO: implement read only 'r' flag as default
        self._memmap = np.memmap(memmap, dtype=np.uint8, mode='w+', shape=self._shape)

    @property
    def buffer(self):
        return self._buffer

    @property
    def last_frame(self):
        # retrieve frame from the memory
        np.copyto(self._last_frame, self._memmap)
        return self._last_frame
        #self._last_frame[:] = self._memmap[:]
        # this works really well but causes other code to fail if they both read and write
        # at the same time
        #return self._memmap[:]

    def add(self, item: np.ndarray):
        try:
            # add frame at index 0 to the memmap
            # if does not exist, we just proceed with appending frame
            self._memmap[:] = self._buffer.popleft()[:]
        except IndexError:
            # TODO: implment logger
            print("ring buffer is empty")
        # if buffer is full it will erase some elements
        # this adds to the right, so we can always read element 0
        self._buffer.append(item)

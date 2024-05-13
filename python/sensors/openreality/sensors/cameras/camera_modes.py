from typing import Tuple

"""
    This class can be universally used to create capture parameters
"""
class CaptureMode:
    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps

    @property
    def parameters(self) -> Tuple[int, int, int]:
        return (self.width, self.height, self.fps)

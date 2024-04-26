import cv2
import numpy as np

# multiprocessing
import multiprocessing
from multiprocessing import shared_memory

class DemoDualCamera(multiprocessing.Process):
    def __init__(self, left_cam: int, right_cam: int):
        super().__init__()
        self._cam_left = left_cam
        self._cam_right = right_cam
        self._width = 1920
        self._height = 1080
        self._fps = 30
        
    def run(self):
        # create capture device
        cap_left = cv2.VideoCapture(self._cam_left)
        cap_left.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap_left.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap_left.set(cv2.CAP_PROP_FPS, self._fps)

        cap_right = cv2.VideoCapture(self._cam_right)
        cap_right.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap_right.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap_right.set(cv2.CAP_PROP_FPS, self._fps)

        # render video
        cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # stream image
        while cap_left.isOpened() and cap_right.isOpened():
            # Get the frame
            ret_left, frame_left = cap_left.read()
            ret_right, frame_right = cap_right.read()

            # Check
            if ret_left and ret_right:
                # rotate each image to show it on the vertically messed up screen
                frame_left = cv2.rotate(frame_left, cv2.ROTATE_90_COUNTERCLOCKWISE)
                frame_right = cv2.rotate(frame_right, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # combine images in a vertical stack (use hstack for horizontal)
                final_render = np.vstack((frame_right, frame_left))

                # create final image on full screen
                cv2.imshow("render", final_render)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # TODO: logging handler
                print("camera capture failed")
        # stop opencv stream
        cap_left.release()
        cap_right.release()

        
# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_cam = DemoDualCamera(left_cam=0, right_cam=1)
    test_cam.start()

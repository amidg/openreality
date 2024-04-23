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
        cam_left: str = "/tmp/cam1",
        cam_right: str = "/tmp/cam2"
    ):
        super().__init__()
        self._cam_left = cam_left
        self._cam_right = cam_right

        # TODO: add programmatic camera characterisitics
        self._cam_width = 1920
        self._cam_height = 1080
        self._cam_fps = 30

        # shared memory device
        self._gst_left = (
            f"shmsrc socket-path={self._cam_left} ! " \
            f"video/x-raw, format=BGR, width={self._cam_width}, height={self._cam_height}, pixel-aspect-ratio=1/1, framerate={self._cam_fps}/1 ! "\
            f"decodebin ! videoconvert ! appsink"
        )

        self._gst_right = (
            f"shmsrc socket-path={self._cam_right} ! " \
            f"video/x-raw, format=BGR, width={self._cam_width}, height={self._cam_height}, pixel-aspect-ratio=1/1, framerate={self._cam_fps}/1 ! "\
            f"decodebin ! videoconvert ! appsink"
        )
         

    def run(self):
        # create capture device
        cap_left = cv2.VideoCapture(self._gst_left, cv2.CAP_GSTREAMER)
        cap_right = cv2.VideoCapture(self._gst_right, cv2.CAP_GSTREAMER)

        # create output device
        cv2.namedWindow("render", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("render", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # TODO: add proper handling
        while cap_left.isOpened() and cap_right.isOpened():
            ret_left, frame_left = cap_left.read()
            ret_right, frame_right = cap_right.read()
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
                break
        cap_left.release()
        cap_right.release()
        cv2.destroyAllWindows()


# demo code to run this separately
if __name__ == "__main__":
    # start device in desired mode
    test_render = Renderer(cam_left="/tmp/cam0", cam_right="/tmp/cam1")
    test_render.start()

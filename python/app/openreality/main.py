from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3
import sys
import os
import numpy as np
import cv2
from multiprocessing import shared_memory

# fullscreen attempt
panda3d.core.load_prc_file_data("", "show-frame-rate-meter #t")
panda3d.core.load_prc_file_data("", "sync-video #f")
#panda3d.core.load_prc_file_data("", "win-size 1920 1080") # 17 fps
#panda3d.core.load_prc_file_data("", "win-size 1280 720") # 25 fps
panda3d.core.load_prc_file_data("", "win-size 2560 1440") # 8 fps
panda3d.core.load_prc_file_data("", "fullscreen 1") # 8 fps

# openreality
from openreality.core.capture import Capture, CameraRotation
from openreality.sensors.camera import Camera

# start create list of cameras
crop_area = (0,720,320,960)
resolution = (1280,720)
cameras = [
    Camera(device=3, resolution=resolution, crop_area=crop_area), # left cam
    Camera(device=1, resolution=resolution, crop_area=crop_area), # right cam
]
capture = Capture(cameras=cameras)
capture.start()

# shared memory
#frame_shape = (resolution[0], resolution[1], 3)
#shm = shared_memory.SharedMemory(name="capture")
#shm_frame = np.ndarray(frame_shape, dtype=np.uint8, buffer=shm.buf)

# game
base = ShowBase()

# generate a frame geometry to apply the camera texture to
cardmaker = panda3d.core.CardMaker("openreality")
cardmaker.set_frame(-base.win.get_x_size(), base.win.get_x_size(), -base.win.get_y_size(), base.win.get_y_size())
frame = panda3d.core.NodePath(cardmaker.generate())
frame.set_scale(frame.get_scale()/ base.win.get_y_size())
frame.set_r(0)
frame.flatten_light() # apply scale
frame.reparent_to(aspect2d)

# camera texture
cv_camera_frame_texture = panda3d.core.Texture()
cv_camera_frame_texture.setup_2d_texture(
    resolution[0],
    resolution[1],
    panda3d.core.Texture.T_unsigned_byte,
    panda3d.core.Texture.F_rgb8
)
frame.set_texture(cv_camera_frame_texture, 1)

def update_usb_camera_frame(task):
    if capture.ready:
        image = cv2.flip(capture.frame, 1)
        cv_camera_frame_texture.set_ram_image(image)
    #if np.any(shm_frame): # check that we have something in the buffer 
    #    image = cv2.flip(shm_frame, 1)
    #    cv_camera_frame_texture.set_ram_image(image)
    return task.again
	
# tasks
base.task_mgr.do_method_later(1/30, update_usb_camera_frame, "update_usb_camera_frame")

# run main game
base.run()

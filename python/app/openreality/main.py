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

# fullscreen attempt
panda3d.core.load_prc_file_data("", "show-frame-rate-meter #t")
panda3d.core.load_prc_file_data("", "sync-video #f")
panda3d.core.load_prc_file_data("", "win-size 2560 1440")
panda3d.core.load_prc_file_data("", "fullscreen 1")

# openreality
from openreality.core.capture import Capture
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

# game
base = ShowBase()

# generate a frame geometry to apply the camera texture to
cardmaker = panda3d.core.CardMaker("openreality")
cardmaker.set_frame(-base.win.get_x_size(), base.win.get_x_size(), -base.win.get_y_size(), base.win.get_y_size())
frame = panda3d.core.NodePath(cardmaker.generate())
frame.set_scale(frame.get_scale()/ base.win.get_y_size())
frame.set_r(90)
frame.flatten_light() # apply scale
frame.reparent_to(aspect2d)

# camera texture
cv_camera_frame_texture = panda3d.core.Texture()
cv_camera_frame_texture.setup_2d_texture(720, 1280, panda3d.core.Texture.T_unsigned_byte, panda3d.core.Texture.F_rgb8)
frame.set_texture(cv_camera_frame_texture, 1)

def update_usb_camera_frame(task):
    if capture.buffer_ready:
        cv_camera_frame_texture.set_ram_image(capture.frame)
    return task.again
	
# tasks
base.task_mgr.do_method_later(1000/60*0.001, update_usb_camera_frame, "update_usb_camera_frame")

# run main game
base.run()

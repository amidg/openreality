import cv2
import panda3d
from direct.showbase.ShowBase import ShowBase
from multiprocessing import shared_memory
panda3d.core.load_prc_file_data("", "show-frame-rate-meter #t")
panda3d.core.load_prc_file_data("", "sync-video #f")

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
capture = Capture(cameras=cameras, rotation=cv2.ROTATE_90_CLOCKWISE)
capture.start()

# game
base = ShowBase()

# generate a frame geometry to apply the camera texture to
cardmaker = panda3d.core.CardMaker("openreality")
cardmaker.set_frame(-base.win.get_x_size(), base.win.get_x_size(), -base.win.get_y_size(), base.win.get_y_size())
frame = panda3d.core.NodePath(cardmaker.generate())
frame.set_scale(frame.get_scale()/ base.win.get_y_size())
frame.set_r(180)
frame.flatten_light() # apply scale
frame.reparent_to(aspect2d)

# camera texture
cv_camera_frame_texture = panda3d.core.Texture()
cv_camera_frame_texture.setup_2d_texture(720, 1280, panda3d.core.Texture.T_unsigned_byte, panda3d.core.Texture.F_rgb8)
frame.set_texture(cv_camera_frame_texture, 1)

def update_usb_camera_frame(task):
    if capture.buffer_ready:
        cv_camera_frame_texture.set_ram_image(capture.frame)
	
# tasks
base.task_mgr.do_method_later(1000/60*0.001, update_usb_camera_frame, "update_usb_camera_frame")

# run main game
base.run()

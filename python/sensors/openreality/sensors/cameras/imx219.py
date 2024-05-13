from openreality.sensors.camera_modes import CaptureMode

"""
    IMX219 camera parameters.
    This can be used for both stereo and single imager models
"""
imx219 = {
    0: CaptureMode(
        width=3264,
        height=2464,
        fps=21
    ),
    1: CaptureMode(
        width=3264,
        height=1848,
        fps=28
    ),
    2: CaptureMode(
        width=1920,
        height=1080,
        fps=30
    ),
    3: CaptureMode(
        width=1640,
        height=1232,
        fps=30
    ),
    4: CaptureMode(
        width=1280,
        height=720,
        fps=60
    ),
}

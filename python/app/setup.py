from setuptools import setup

setup(
    name="openreality.app",
    packages=[
        "openreality.app.core", # core apps, e.g. capture, render, etc
        "openreality.app.simple" # simple display app
    ],
    version="0.0.1",
    install_requires=[
        # OpenReality packages
        "openreality.sensors",
        "openreality.sdk",
        # System packages, e.g. mediapipe
        # Default packages that should be included by default
        # these can probably be removed
        "opencv-contrib-python==4.9.0.80+openreality",
        "numpy==1.19.4",
        "pyzmq"
    ],
    entry_points={
        "console_scripts": [
            "openreality = openreality.app.simple.main:main"
        ]
    },
)

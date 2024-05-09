from setuptools import setup

setup(
    name="openreality.sensors",
    packages=["openreality.sensors"],
    version="0.0.1",
    install_requires=[
        "opencv-contrib-python==4.9.0.80+openreality",
        "numpy==1.19.4",
    ],
    entry_points={
        "console_scripts": ["demo_camera = openreality.sensors.jetson_camera:main"]
    },
)

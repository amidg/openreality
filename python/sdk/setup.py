from setuptools import setup

setup(
    name="openreality.sdk",
    packages=["openreality.sdk"],
    version="0.0.1",
    install_requires=[
        "opencv-contrib-python==4.9.0.80+openreality",
        "numpy==1.19.4",
    ],
    entry_points={
        "console_scripts": [
            "demo_client = openreality.sdk.camera:main",
            "demo_server = openreality.sdk.stereo_camera:main",
        ]
    },
)

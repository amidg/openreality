from setuptools import setup

setup(
    name="openreality.sdk",
    packages=["openreality.sdk"],
    version="0.0.1",
    install_requires=[
        # 1.19.4 is required when using Jetson Nano
        "numpy>=1.19.4", # framebuffer
        "pyzmq", # ipc
        "tomli" # config
    ],
)

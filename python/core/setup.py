from setuptools import setup

setup(
    name="openreality.core",
    packages=["openreality.core"],
    version="0.0.1",
    install_requires=[
        "opencv-contrib-python==4.9.0.80+openreality",
        "numpy==1.19.4",
        "pyzmq",
    ],
    entry_points={
        "console_scripts": [
            "openreality_core_app = openreality.core.capture:main"
        ]
    },
)

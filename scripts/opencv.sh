#!/bin/bash

#SCRIPT_DIR="$(dirname "$0")"
#pushd $SCRIPT_DIR
#./setup-python.sh

OPENCV_VERSION="80"
MAKEFLAGS="-j$(nproc)" # enable all core builds

# Clone opencv repo, using a specific version branch that we want.
# This version is incorporated into the wheel version and is important
git clone --recursive https://github.com/opencv/opencv-python.git --branch "$OPENCV_VERSION"
cd opencv-python

# Now re-tag the repository with +industrialnext
git tag "$OPENCV_VERSION+openreality"
# Now remove the old tag
git tag -d "$OPENCV_VERSION"

echo "Building opencv $OPENCV_VERSION (tags are $(git describe --tags))"

export MAKEFLAGS="-j$(nproc)"
export CMAKE_ARGS="-DWITH_GSTREAMER=ON -DWITHFFMPEG=ON -DOPENCV_ENABLE_NONFREE=OFF -DWITH_FREETPYE=ON -DWITH_GTK=ON -DWITH_QT=ON -DWITH_V4L=ON -DWITH_OPENGL=ON"
export ENABLE_CONTRIB="1"

python3 -m pip wheel . --verbose
#python3 -m twine upload -r local opencv*.whl --config-file ~/.pypirc

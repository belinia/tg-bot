#!/usr/bin/env bash
# Hata olursa dur
set -o errexit

# FFmpeg kurulumu
mkdir -p ffmpeg
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar xJ -C ffmpeg --strip-components 1
export PATH=$PATH:$(pwd)/ffmpeg

# Python paketlerini kur
pip install -r requirements.txt

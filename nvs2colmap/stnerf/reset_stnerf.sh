#!/bin/bash
set -e
rm -rf data/boxing data/taekwondo data/walking
mkdir -p data/boxing data/taekwondo data/walking
ln data/boxing.zip data/boxing/boxing.zip
ln data/taekwondo.zip data/taekwondo/taekwondo.zip
ln data/walking.zip data/walking/walking.zip
python -m nvs2colmap.stnerf --path data/taekwondo --n-frames 101 "$@"
python -m nvs2colmap.stnerf --path data/walking --n-frames 75 "$@"

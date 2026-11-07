#!/bin/bash
set -e
rm -rf data/discussion data/trimming data/stepin data/vrheadset
unzip -d data data/discussion.zip
unzip -d data data/trimming.zip
unzip -d data data/stepin.zip
unzip -d data data/vrheadset.zip
python -m nvs2colmap.n3dv --path data/discussion "$@"
python -m nvs2colmap.n3dv --path data/trimming "$@"
python -m nvs2colmap.n3dv --path data/stepin "$@"
python -m nvs2colmap.n3dv --path data/vrheadset "$@"

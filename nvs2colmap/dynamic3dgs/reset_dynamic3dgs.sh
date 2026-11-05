#!/bin/bash
rm -rf data/basketball data/boxes data/football data/juggle data/softball data/tennis
unzip data/data.zip
python -m nvs2colmap.dynamic3dgs --path data/basketball --n-frames 150 "$@"
python -m nvs2colmap.dynamic3dgs --path data/boxes --n-frames 150 "$@"
python -m nvs2colmap.dynamic3dgs --path data/football --n-frames 150 "$@"
python -m nvs2colmap.dynamic3dgs --path data/juggle --n-frames 150 "$@"
python -m nvs2colmap.dynamic3dgs --path data/softball --n-frames 150 "$@"
python -m nvs2colmap.dynamic3dgs --path data/tennis --n-frames 150 "$@"

#!/bin/bash
set -e
rm -rf data/basketball data/boxes data/football data/juggle data/softball data/tennis
unzip data/data.zip
python -m nvs2colmap.dynamic3dgs --path data/basketball "$@"
python -m nvs2colmap.dynamic3dgs --path data/boxes "$@"
python -m nvs2colmap.dynamic3dgs --path data/football "$@"
python -m nvs2colmap.dynamic3dgs --path data/juggle "$@"
python -m nvs2colmap.dynamic3dgs --path data/softball "$@"
python -m nvs2colmap.dynamic3dgs --path data/tennis "$@"

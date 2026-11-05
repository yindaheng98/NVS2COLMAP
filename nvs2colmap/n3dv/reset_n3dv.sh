#!/bin/bash
set -e
rm -rf data/coffee_martini data/cook_spinach data/cut_roasted_beef data/flame_salmon_1 data/flame_steak data/sear_steak
(
  cd data
  zip -F flame_salmon_1_split.zip --out flame_salmon_1.zip
)
unzip -d data data/coffee_martini.zip
unzip -d data data/cook_spinach.zip
unzip -d data data/cut_roasted_beef.zip
unzip -d data data/flame_steak.zip
unzip -d data data/sear_steak.zip
unzip -d data data/flame_salmon_1.zip
python -m nvs2colmap.n3dv --path data/coffee_martini --n-frames 300 "$@"
python -m nvs2colmap.n3dv --path data/cook_spinach --n-frames 300 "$@"
python -m nvs2colmap.n3dv --path data/cut_roasted_beef --n-frames 300 "$@"
python -m nvs2colmap.n3dv --path data/flame_salmon_1 --n-frames 1200 "$@"
python -m nvs2colmap.n3dv --path data/flame_steak --n-frames 300 "$@"
python -m nvs2colmap.n3dv --path data/sear_steak --n-frames 300 "$@"

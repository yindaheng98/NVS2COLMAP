#!/bin/bash
set -e
tar -xf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar \
  -C data/SiggraphAsia2026VVC \
  --transform 's,^SiggraphAisa2026VVC_heldout_test_cameras/,,' \
  --transform 's,\([^/]*\)/\([^/]*\)$,\1.tar/\1/\2,' \
  --wildcards '*/test_intri.yml' '*/test_extri.yml'
rm -rf \
  data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0
mkdir -p \
  data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0.tar/004_1_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0.tar/006_1_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0.tar/007_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0.tar/009_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0.tar/011_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0.tar/001_1_seq0/. data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0.tar/012_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0/
# siga sparse
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0 "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0 "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0 "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0 "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0 "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0 "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0 "$@"

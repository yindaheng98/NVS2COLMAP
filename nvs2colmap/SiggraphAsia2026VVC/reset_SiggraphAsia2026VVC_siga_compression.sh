#!/bin/bash
set -e
tar -xf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar \
  -C data/SiggraphAsia2026VVC \
  --transform 's,^SiggraphAisa2026VVC_heldout_test_cameras/,,' \
  --transform 's,\([^/]*\)/\([^/]*\)$,\1.tar/\1/\2,' \
  --wildcards '*/test_intri.yml' '*/test_extri.yml'
rm -rf \
  data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0
mkdir -p \
  data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0
cp -al data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1.tar/004_1_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1.tar/006_1_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1.tar/007_0_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1.tar/008_2_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1.tar/011_0_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0.tar/001_1_seq0/. data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0.tar/012_0_seq0/. data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0/
# siga exclude close view
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 --include-cameras '{*range(0,25),*range(26,28),31,36,*range(43,46),*range(49,51)}' "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1 --include-cameras '{*range(0,26),*range(27,29),32,37,*range(44,47),*range(50,52)}' "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1 --include-cameras '{*range(0,27),*range(28,30),33,38,*range(45,48),*range(51,53)}' "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1 --include-cameras '{*range(0,26),*range(27,29),32,*range(43,46),*range(49,51)}' "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1 --include-cameras '{*range(0,27),*range(28,30),33,38,*range(45,48),*range(51,53)}' "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0 --include-cameras '{*range(0,27),*range(28,30),33,38,*range(45,48),*range(51,53)}' "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0 --include-cameras '{*range(0,27),*range(28,30),33,38,*range(45,48),*range(51,53)}' "$@"

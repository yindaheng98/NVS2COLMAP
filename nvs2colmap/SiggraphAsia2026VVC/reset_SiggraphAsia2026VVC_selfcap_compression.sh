#!/bin/bash
set -e
tar -xf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar \
  -C data/SiggraphAsia2026VVC \
  --transform 's,^SiggraphAisa2026VVC_heldout_test_cameras/,,' \
  --transform 's,\([^/]*\)/\([^/]*\)$,\1.tar/\1/\2,' \
  --wildcards '*/test_intri.yml' '*/test_extri.yml'
rm -rf \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga
mkdir -p \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga
cp -al data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike.tar/0512_bike/. data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike/
cp -al data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi.tar/0525_corgi/. data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi/
cp -al data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga.tar/0811_yoga/. data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga/
# selfcap
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi "$@"
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga "$@"

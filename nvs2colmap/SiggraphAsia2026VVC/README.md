# Siggraph Asia 2026 Volumetric Video Challenge

This package converts scenes from the **Siggraph Asia 2026 Volumetric Video
Challenge** into per-frame COLMAP outputs. By default it writes COLMAP text
models. Views whose distortion is zero are hardlinked. Views with a nonzero
`D_<view>` keep a hardlink of the original in `input/`. COLMAP's
`image_undistorter` writes `images/` and a `PINHOLE` model fitted to that
image. Included masks follow the images. With `--use-colmap`, it runs the full
COLMAP pipeline on every extracted frame.

## Supported Datasets

- **Siggraph Asia 2026 VVC**: dataset
  [zju3dv/SiggraphAsia2026VVC](https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC).
  The public release contains the `siga` and `selfcap` tracks. The camera YAML
  is the EasyVolCap layout used by the previous challenge release and by
  [TrackerSplat's SIGA2025 loader](https://github.com/yindaheng98/TrackerSplat/blob/SIGA2025VVC/tools/parse_camera_SIGA2025VVC.py).

The dataset is gated and about 309 GB. Request access on the dataset page,
then log in with `hf auth login`.

Runtime dependencies:

```bash
pip install numpy pillow torch
pip install -U huggingface_hub
```

## Quick Start

Each scene is one tar. `curl` pipes it into `tar`, so the archive is not stored.
The archive keeps its scene directory, so the files land at
`data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1.tar/004_1_seq1`.
Those `.tar` directories stay as downloaded. `release_manifest.json` lists the
public views. The held-out camera package is downloaded here and unpacked below.

```bash
mkdir -p \
  data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1.tar \
  data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1.tar \
  data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1.tar \
  data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1.tar \
  data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1.tar \
  data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0.tar \
  data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0.tar \
  data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0.tar \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike.tar \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi.tar \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga.tar \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike.tar \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi.tar \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga.tar
hf auth login
hf download zju3dv/SiggraphAsia2026VVC --type dataset --local-dir data/SiggraphAsia2026VVC --include "license.txt" --include "checksums.sha256" --include "release_manifest.json" --include "archive_manifest.json" --include "heldout_test_cameras/*"
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/004_1_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/006_1_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/007_0_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/008_2_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/011_0_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/val/001_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/val/012_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/004_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/006_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/007_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/009_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/011_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/val/001_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/val/012_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/compression/test/0512_bike.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/compression/test/0525_corgi.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/compression/test/0811_yoga.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/sparse/test/0512_bike.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/sparse/test/0525_corgi.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi.tar
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/sparse/test/0811_yoga.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga.tar
```

Each archive starts with the scene directory, for example `004_1_seq1/images/`.
`checksums.sha256` lists the uploaded archives; those tar files are not kept.

The held-out package is small and has camera YAML and no images.
`heldout_test_cameras/checksums.sha256` checks that archive. Extract it so
`test_intri.yml` and `test_extri.yml` land in each `.tar` scene directory.
List the archive first. The transforms drop a leading `SiggraphAisa2026VVC/`
prefix when it is present, and insert `.tar` before the scene directory, so
`004_1_seq1/test_intri.yml` lands at `004_1_seq1.tar/004_1_seq1/test_intri.yml`.
Hardlink every extracted file into the scene directory passed to `--path`.
Remove only those scene directories first. That deletes generated frames and
leaves the files in the `.tar` directories.

```bash
tar -tf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar | head
tar -xf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar \
  -C data/SiggraphAsia2026VVC \
  --transform 's,^SiggraphAisa2026VVC/,,' \
  --transform 's,\([^/]*\)/\([^/]*\)$,\1.tar/\1/\2,'
rm -rf \
  data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0 \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga
mkdir -p \
  data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1 \
  data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0 \
  data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0 \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi \
  data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi \
  data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga
cp -al data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1.tar/004_1_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1.tar/006_1_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1.tar/007_0_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1.tar/008_2_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1.tar/011_0_seq1/. data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1/
cp -al data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0.tar/001_1_seq0/. data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0.tar/012_0_seq0/. data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0.tar/004_1_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0.tar/006_1_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0.tar/007_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0.tar/009_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0.tar/011_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0.tar/001_1_seq0/. data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0/
cp -al data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0.tar/012_0_seq0/. data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0/
cp -al data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike.tar/0512_bike/. data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike/
cp -al data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi.tar/0525_corgi/. data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi/
cp -al data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga.tar/0811_yoga/. data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga/
cp -al data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike.tar/0512_bike/. data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike/
cp -al data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi.tar/0525_corgi/. data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi/
cp -al data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga.tar/0811_yoga/. data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga/
```

Link images and masks, then write COLMAP text models. The default run starts
at the first frame file and writes `frame1`. `siga` frames begin at
`000000.jpg`. `selfcap` releases `000900.jpg` through `001799.jpg`, and
`000900.jpg` is still `frame1`.

```bash
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/006_1_seq1
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/007_0_seq1
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/008_2_seq1
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/test/011_0_seq1
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/compression/val/012_0_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/004_1_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/006_1_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/007_0_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/009_0_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/test/011_0_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/val/001_1_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/siga/sparse/val/012_0_seq0
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/compression/test/0512_bike
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/compression/test/0525_corgi
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/compression/test/0811_yoga
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0525_corgi
python -m nvs2colmap.SiggraphAsia2026VVC --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0811_yoga
```

## Dataset Format

A scene folder contains one directory of frames per view, EasyVolCap camera
YAML, and optional masks and point clouds:

```text
004_1_seq1/
  images/
    00/000000.jpg
    00/000001.jpg
    01/000000.jpg
    ...
  masks/
    00/000000.png
    00/000001.png
    ...
  train_intri.yml
  train_extri.yml
  test_intri.yml
  test_extri.yml
  intri.yml
  extri.yml
  t_offsets.json
  pcds/
    000000.ply
```

Frames are `.jpg`. Output folders count those files from `frame1`, so the
first file is `frame1` whether its name is `000000.jpg` or `000900.jpg`.

`train_intri.yml` and `train_extri.yml` are the training views.
`test_intri.yml` and `test_extri.yml` are the test views, and are read when
those files are present. A view without `images/<view>/` is left out. A view
listed in both YAML files keeps the training record. Views are sorted by name,
so `images/00/000000.jpg` becomes `00.jpg`. `--include-cameras` and `--exclude-cameras`
keep or drop those view ids. The number `0` matches `00` and `0000`.

Each YAML pair stores:

- `names`: view ids, such as `00` and `01`.
- `K_<view>`: 3 x 3 intrinsic matrix. `fx`, `fy`, `cx`, and `cy` are read from
  it. Image width and height come from the JPEG, not from `W_<view>` and
  `H_<view>`. COLMAP 3.13 rejects a model whose camera size does not match the
  image file.
- `R_<view>`: Rodrigues rotation of the world-to-camera pose.
- `T_<view>`: world-to-camera translation. The pose is already in the COLMAP
  camera convention.
- `D_<view>`: OpenCV distortion coefficients `k1 k2 p1 p2 k3`. An all-zero
  vector is left out. Any other value is written as COLMAP `OPENCV` using
  `k1 k2 p1 p2`, and COLMAP undistorts `input/` into `images/`. The saved
  camera is the resulting `PINHOLE` model.

`t_offsets.json` stores a per-view time offset. The converter leaves it out of
the COLMAP files. `pcds/000000.ply`, when present, is hardlinked to
`sparse/0/points3D.ply` in every extracted frame.

## Output Format

In the default mode, each frame directory contains images, any masks, and a
COLMAP text model. Zero-distortion images and masks are hardlinks. A scene with
nonzero distortion also keeps the original files:

```text
0512_bike/
  frame1/
    input/
      0002.jpg
      ...
    images/
      0002.jpg
      ...
    input_mask/
      0002.jpg.png
      ...
    image_masks/
      0002.jpg.png
      ...
    sparse/0/
      cameras.txt
      images.txt
      points3D.txt
      points3D.ply
```

`input/` is a hardlink of the source image. `images/` is the file written by
COLMAP's `image_undistorter`. A zero-distortion scene has no `input/` in the
default mode; its hardlinks are only in `images/` and `image_masks/`.
Mask filenames keep the image filename and add `.png`, so `images/0002.jpg`
pairs with `image_masks/0002.jpg.png`, and `input/0002.jpg` pairs with
`input_mask/0002.jpg.png`. A view with no `masks/<view>/` file gets an image
and no mask. When `pcds/` is missing, `points3D.ply` is omitted.
`--use-colmap` leaves the reconstructed points in `distorted/sparse/0` and
does not link `pcds/`.

With `--use-colmap`, images are linked into `frame*/input` and masks into
`frame*/input_mask` (`input/0002.jpg` pairs with `input_mask/0002.jpg.png`).
Each frame then runs feature extraction, matching, triangulation, mapping,
`image_undistorter`, and `mask_undistorter`. Undistorted images are written to
`images/`, and undistorted masks to `image_masks/`.

All generated camera models use `PINHOLE`. Every camera gets its own COLMAP
camera ID because these scenes are multi-view captures with known poses and
per-view intrinsics. IDs start at 1 in view-name order.

## Usage

Link images and masks, then write COLMAP text models:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1
```

Start at source frame `000009.jpg`. Output folders are still `frame1`, `frame2`, ...:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  --start-number 10 \
  --n-frames 20
```

Keep every third source frame. Output folders stay `frame1`, `frame2`, ...:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike \
  --frame-skip 3 \
  --n-frames 300
```

`selfcap` sparse scenes such as `0512_bike` have no `masks/` and no
`test_*.yml`. The released frames are `000900.jpg` through `001799.jpg`, and
the default command writes them as `frame1` through `frame900`:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike
```

Extract only the training cameras:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/val/001_1_seq0 \
  --no-test-camera
```

Leave out close-up cameras by view id. The value is a Python expression of
ints. This drops views `25`, `28`, `29`, and `30`:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  --exclude-cameras '{25, *range(28, 31)}'
```

Keep an explicit set instead:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike \
  --include-cameras 2,4,8
```

Run the full COLMAP pipeline for each frame:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" \
  --colmap-use-gpu 1
```

## Important Options

- `--path`: scene directory containing `images/`, `train_intri.yml`, and
  `train_extri.yml`.
- `--n-frames`: number of frames to extract and write after `--frame-skip`.
  If omitted, every kept frame from `--start-number` through the last frame
  on disk is used. A value past the frames that remain writes those frames.
- `--no-train-camera`: skip cameras listed in `train_intri.yml` and
  `train_extri.yml`.
- `--no-test-camera`: skip cameras listed in `test_intri.yml` and
  `test_extri.yml`.
- `--include-cameras`: Python expression of camera numbers to keep, such as
  `0,1,11` or `range(0, 25)`. Every value must be an int. A number matches the
  YAML view name, so `0` selects `00` and `0000`. Defaults to every camera in
  the selected split.
- `--exclude-cameras`: Python expression of camera numbers to leave out, in
  the same form as `--include-cameras`. Close-up views can be dropped this
  way. Applied after `--include-cameras`. A number with no matching view is
  left out.
- `--start-number`: 1-based position in the frames on disk, default `1`.
  The first file is source frame 1. Output folders are renumbered from `frame1`.
- `--frame-skip`: keep every Nth source frame after `--start-number`, default
  `1`. Output folders stay `frame1`, `frame2`, ...
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable. Nonzero distortion uses
  it for `image_undistorter`, and `--use-colmap` uses it for the full pipeline.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.

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
pip install numpy torch
pip install -U huggingface_hub
```

## Quick Start

Each scene is one tar. `curl` pipes it into `tar`, so the archive is not stored.
`tar` overwrites files already in the scene directory. `release_manifest.json`
lists the public views.

```bash
mkdir -p data/SiggraphAsia2026VVC/siga/{compression,sparse}/{test,val} data/SiggraphAsia2026VVC/selfcap/{compression,sparse}/test
hf auth login
hf download zju3dv/SiggraphAsia2026VVC --type dataset --local-dir data/SiggraphAsia2026VVC --include "license.txt" --include "checksums.sha256" --include "release_manifest.json" --include "archive_manifest.json" --include "heldout_test_cameras/*"
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/004_1_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/006_1_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/007_0_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/008_2_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/test/011_0_seq1.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/val/001_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/val
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/compression/val/012_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/compression/val
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/004_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/006_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/007_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/009_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/test/011_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/val/001_1_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/val
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/siga/sparse/val/012_0_seq0.tar | tar -xf - -C data/SiggraphAsia2026VVC/siga/sparse/val
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/compression/test/0512_bike.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/compression/test/0525_corgi.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/compression/test/0811_yoga.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/compression/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/sparse/test/0512_bike.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/sparse/test/0525_corgi.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/sparse/test
curl -fL -H "Authorization: Bearer $(hf auth token)" https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC/resolve/main/selfcap/sparse/test/0811_yoga.tar | tar -xf - -C data/SiggraphAsia2026VVC/selfcap/sparse/test
```

Each archive starts with the scene directory, for example `004_1_seq1/images/`.
`checksums.sha256` lists the uploaded archives; those tar files are not kept.

The held-out package is small and has camera YAML and no images.
`heldout_test_cameras/checksums.sha256` checks that archive. Extract it so
`test_intri.yml` and `test_extri.yml` land in each scene directory. List the
archive first. When the first path component is `siga/` or `selfcap/`, extract
at the dataset root. When it is `SiggraphAisa2026VVC/`, add
`--strip-components=1`.

```bash
tar -tf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar | head
tar -xf data/SiggraphAsia2026VVC/heldout_test_cameras/SiggraphAisa2026VVC_heldout_test_cameras.tar \
  -C data/SiggraphAsia2026VVC
```

Link images and masks, then write COLMAP text models. The default run starts
at the first frame file. `siga` frames begin at `000000.jpg`, which is
`frame1`. `selfcap` releases `000900.jpg` through `001799.jpg`, so the first
output directory is `frame901`.

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

Images are `.jpg` or `.png`. A view keeps one suffix for every frame. The
frame stem is a zero-padded index, so `000000.jpg` is output frame `1` and
`000900.jpg` is output frame `901`.

`train_intri.yml` and `train_extri.yml` are the training views.
`test_intri.yml` and `test_extri.yml` are the test views. Public test scenes
omit the held-out test images and the held-out test camera files. After the
held-out package is extracted, a test view is written only when
`images/<view>/` exists. `intri.yml` and `extri.yml` are the released views
together; the converter reads them when the `train_*.yml` pair is absent.

A view listed in both the train and test YAML is written once. The two records
must agree. Views are sorted by name, so image `images/00/000000.jpg` becomes
`00.jpg`.

Each YAML pair stores:

- `names`: view ids, such as `00` and `01`.
- `K_<view>`: 3 x 3 intrinsic matrix. `fx`, `fy`, `cx`, and `cy` are read from
  it.
- `H_<view>`, `W_<view>`: image height and width when they are positive. Zero
  and negative values mean the size is read from the image file.
- `R_<view>`: Rodrigues rotation of the world-to-camera pose. `Rot_<view>` is
  used when `R_<view>` is absent.
- `T_<view>`: world-to-camera translation. The pose is already in the COLMAP
  camera convention.
- `D_<view>`: OpenCV distortion coefficients. A zero vector is ignored and the
  image is hardlinked. A nonzero vector is written into an `OPENCV` model, and
  COLMAP undistorts `input/` into `images/`. The saved camera is the resulting
  `PINHOLE` model.

`t_offsets.json` stores a per-view time offset. The converter leaves it out of
the COLMAP files. `pcds/` is optional. `pcds/000000.ply` is a shared init
cloud. `pcds/000001.ply` and the other indexed clouds belong to that source
frame.

## Output Format

In the default mode, each frame directory contains images, any masks, and a
COLMAP text model. Zero-distortion images and masks are hardlinks. A scene with
nonzero distortion also keeps the original files:

```text
0512_bike/
  frame901/
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

Start at source frame `000009.jpg` and keep output frame numbering aligned
with it:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  --start-number 10 \
  --n-frames 20
```

`selfcap` sparse scenes such as `0512_bike` have no `masks/` and no
`test_*.yml`. The released frames are `000900.jpg` through `001799.jpg`, and
the default command writes `frame901` through `frame1800`:

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

Run the full COLMAP pipeline for each frame:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable colmap \
  --colmap-use-gpu 1
```

Reuse existing linked frame images:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1 \
  --skip-frame-linking
```

## Important Options

- `--path`: scene directory containing `images/`, `train_intri.yml`, and
  `train_extri.yml`.
- `--n-frames`: number of frames to extract and write. If omitted, every frame
  from `--start-number` through the last frame on disk is used. If omitted
  with `--skip-frame-linking`, frame directories are counted from `frame%d`.
- `--no-train-camera`: skip cameras listed in `train_intri.yml` and
  `train_extri.yml`.
- `--no-test-camera`: skip cameras listed in `test_intri.yml` and
  `test_extri.yml`.
- `--start-number`: 1-based source frame index to start from. The default is
  the first frame file in `images/`. Output `frame%d` folders use that same
  numbering. Source file `000000.jpg` is frame `1`, and `000900.jpg` is frame
  `901`.
- `--skip-frame-linking`: keep existing frame images and masks, and skip
  hardlinking and the distortion undistortion. A zero-distortion scene reuses
  `frame*/images`, or `frame*/input` with `--use-colmap`. A scene with nonzero
  distortion reuses `frame*/input` and the `images/` already written by COLMAP.
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable. Nonzero distortion uses
  it for `image_undistorter`, and `--use-colmap` uses it for the full pipeline.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.

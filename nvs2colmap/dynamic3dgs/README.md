# Dynamic 3D Gaussians

This package converts scenes in the **Dynamic 3D Gaussians** format into
per-frame COLMAP outputs. By default it hardlinks the dataset images, hardlinks
the included masks, and writes COLMAP text models. With `--use-colmap`, it runs
the full COLMAP pipeline on every extracted frame.

## Supported Datasets

- **Dynamic 3D Gaussians**: dataset
  [JonathonLuiten/Dynamic3DGaussians](https://github.com/JonathonLuiten/Dynamic3DGaussians),
  paper
  [Dynamic 3D Gaussians: Tracking by Persistent Dynamic View Synthesis](https://arxiv.org/abs/2308.09713).

Runtime dependencies:

```bash
pip install numpy plyfile torch
```

## Quick Start

The official archive already contains a top-level `data/` directory. Overwrite
`data/data.zip` if it already exists. That zip stays as downloaded:

```bash
mkdir -p data
wget -O data/data.zip https://omnomnom.vision.rwth-aachen.de/data/Dynamic3DGaussians/data.zip
```

Remove only the scenes this archive will replace, then extract from the
repository root so the scenes land at `data/boxes`, `data/basketball`, and the
other sequence folders:

```bash
rm -rf data/basketball data/boxes data/football data/juggle data/softball data/tennis
unzip data/data.zip
```

Link images and masks, then write COLMAP text models. Each scene is one command:

```bash
python -m nvs2colmap.dynamic3dgs --path data/basketball --n-frames 150
python -m nvs2colmap.dynamic3dgs --path data/boxes --n-frames 150
python -m nvs2colmap.dynamic3dgs --path data/football --n-frames 150
python -m nvs2colmap.dynamic3dgs --path data/juggle --n-frames 150
python -m nvs2colmap.dynamic3dgs --path data/softball --n-frames 150
python -m nvs2colmap.dynamic3dgs --path data/tennis --n-frames 150
```

## Dataset Format

A scene folder is expected to contain `train_meta.json`, `test_meta.json`,
images under `ims/`, and foreground masks under `seg/`:

```text
basketball/
  train_meta.json
  test_meta.json
  ims/
    1/000000.jpg
    2/000000.jpg
    ...
  seg/
    1/000000.png
    2/000000.png
    ...
  init_pt_cld.npz
```

`train_meta.json` and `test_meta.json` use the same layout. Each stores one
image size and, for every frame, the same intrinsics, world-to-camera poses,
and camera ids. The converter checks that those values do not change and writes
one static camera list into every output frame. Only the image filename changes
with the frame index.

- `w`, `h`: image width and height.
- `k[frame][camera]`: 3 x 3 intrinsic matrix. `fx`, `fy`, `cx`, and `cy` are read
  from the first frame.
- `w2c[frame][camera]`: 4 x 4 world-to-camera matrix, already in the COLMAP
  camera convention. The first frame is used for every output frame.
- `fn[frame][camera]`: path relative to `ims/`, such as `1/000000.jpg`. The
  matching mask, when the dataset provides one, is `seg/1/000000.png`.
- `cam_id[frame][camera]`: dataset camera id. Output images are named from this
  id, so source image `11/000000.jpg` becomes `cam11.jpg`.

By default every camera in both files is extracted, sorted by `cam_id`. Pass
`--no-train-camera` or `--no-test-camera` to drop one split. Cameras without a
`seg/` mask are still extracted, and no mask file is written for them.
Source frame `000000` is output frame `1`.

## Output Format

In the default mode, each frame directory contains hardlinked images, hardlinked
masks, and a COLMAP text model:

```text
basketball/
  frame1/
    images/
      cam01.jpg
      cam02.jpg
      ...
    image_masks/
      cam01.jpg.png
      cam02.jpg.png
      ...
    sparse/0/
      cameras.txt
      images.txt
      points3D.txt
      points3D.ply
  frame2/
    ...
```

`init_pt_cld.npz` stores xyz and rgb in the first six columns. Without
`--use-colmap`, those points are written to `sparse/0/points3D.ply` and
hardlinked into every extracted frame. `--use-colmap` leaves the reconstructed
points in `distorted/sparse/0` and does not write this ply.
Mask filenames keep the image filename and add `.png`, so `images/cam01.jpg`
pairs with `image_masks/cam01.jpg.png`.

With `--use-colmap`, images are linked into `frame*/input` and masks into
`frame*/input_mask` (`input/cam01.jpg` pairs with `input_mask/cam01.jpg.png`).
Each frame then runs feature extraction, matching, triangulation, mapping,
`image_undistorter`, and `mask_undistorter`. Undistorted images are written to
`images/`, and undistorted masks to `image_masks/`
(`image_masks/cam01.jpg.png`).

All generated camera models use `PINHOLE`. Every camera gets its own COLMAP
camera ID because these scenes are multi-view captures with known poses and
per-view intrinsics.

## Usage

Link images and masks, then write COLMAP text models:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --n-frames 150
```

Start from source frame 10. Output folders are still `frame1`, `frame2`, ...:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --start-number 10 \
  --n-frames 20
```

Run the full COLMAP pipeline for each frame:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --n-frames 150 \
  --use-colmap \
  --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" \
  --colmap-use-gpu 1
```

Extract only the training cameras:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --no-test-camera
```

## Important Options

- `--path`: scene directory containing `train_meta.json`, `test_meta.json`,
  `ims/`, and `seg/`.
- `--n-frames`: number of frames to extract and write after `--frame-skip`.
  If omitted, every kept frame from `--start-number` through the last frame
  in the camera metadata is used. A value past the frames that remain writes
  those frames.
- `--no-train-camera`: skip cameras listed in `train_meta.json`.
- `--no-test-camera`: skip cameras listed in `test_meta.json`.
- `--start-number`: 1-based source frame index to start from, default `1`.
  Source file `000000.jpg` is source frame 1. Output folders are renumbered
  from `frame1`.
- `--frame-skip`: keep every Nth source frame after `--start-number`, default
  `1`. Output folders stay `frame1`, `frame2`, ...
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable used with
  `--use-colmap`.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.

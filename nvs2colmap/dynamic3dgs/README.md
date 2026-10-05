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
pip install numpy torch
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
`seg/` mask are still extracted, and no `image_masks` file is written for them.
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
  frame2/
    ...
```

Mask filenames keep the image filename and add `.png`, so `images/cam01.jpg`
pairs with `image_masks/cam01.jpg.png`.

With `--use-colmap`, images are linked into `frame*/input` instead of
`frame*/images`. Masks stay in `frame*/image_masks`. Each frame then gets the
usual COLMAP workspace outputs after feature extraction, matching,
triangulation, mapping, and undistortion.

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

Start from source frame 10 and keep output frame numbering aligned with it:

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
  --colmap-executable colmap \
  --colmap-use-gpu 1
```

Extract only the training cameras:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --no-test-camera
```

Reuse existing linked frame images:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --skip-frame-linking
```

## Important Options

- `--path`: scene directory containing `train_meta.json`, `test_meta.json`,
  `ims/`, and `seg/`.
- `--n-frames`: number of frames to extract and write. If omitted, every frame
  listed in the camera metadata is used. If omitted with `--skip-frame-linking`,
  frame directories are counted from `frame%d`.
- `--no-train-camera`: skip cameras listed in `train_meta.json`.
- `--no-test-camera`: skip cameras listed in `test_meta.json`.
- `--start-number`: 1-based source frame index to start from, default `1`.
  Output `frame%d` folders use the same numbering. Source file `000000.jpg` is
  frame `1`.
- `--skip-frame-linking`: keep existing frame images and masks, and skip
  hardlinking. In the default mode this reuses `frame*/images`; with
  `--use-colmap` it reuses `frame*/input`.
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable used with
  `--use-colmap`.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.

# ST-NeRF

This package converts scenes in the **ST-NeRF** format into per-frame COLMAP
outputs. It reads the one zip file in the scene directory. By default it
extracts images to `frame*/images` and writes COLMAP text models from
`pose/K.txt` and `pose/RT_c2w.txt`. With `--use-colmap`, it extracts images
to `frame*/input` and runs the full COLMAP pipeline on every frame. A scene
without those pose files raises an error.

## Supported Datasets

- **ST-NeRF**: code
  [DarlingHang/ST-NeRF](https://github.com/DarlingHang/ST-NeRF),
  paper
  [Editable Free-Viewpoint Video using a Layered Neural Representation](https://arxiv.org/abs/2104.14786),
  project page
  [jiakai-zhang.github.io/st-nerf](https://jiakai-zhang.github.io/st-nerf/).

The archives are `walking.zip` (about 10.7 GB), `taekwondo.zip` (about 4.5 GB),
and `boxing.zip` (about 3.3 GB). The folder linked from the ST-NeRF README is
[Documents/st-nerf](https://hkustconnect-my.sharepoint.com/:f:/g/personal/xliufe_connect_ust_hk/EjqArjZxmmtDplj_IrwlUq0BMUyG69zr5YqXFBxgku4rRQ?e=n2fSBs).

Runtime dependencies:

```bash
pip install numpy torch
```

## Quick Start

SharePoint does not publish a direct file URL. Visit the sharing link once to
store a guest cookie, then download each archive with that cookie. Overwrite
the zip files in `data/` if they already exist. Those zip files stay as
downloaded:

```bash
mkdir -p data
cookie=$(mktemp)
share='https://hkustconnect-my.sharepoint.com/:f:/g/personal/xliufe_connect_ust_hk/EjqArjZxmmtDplj_IrwlUq0BMUyG69zr5YqXFBxgku4rRQ?e=n2fSBs'
curl -c "$cookie" -b "$cookie" -L -o /dev/null "$share"
base='https://hkustconnect-my.sharepoint.com/personal/xliufe_connect_ust_hk/_layouts/15/download.aspx?SourceUrl='
curl -c "$cookie" -b "$cookie" -L -o data/boxing.zip \
  "${base}%2Fpersonal%2Fxliufe_connect_ust_hk%2FDocuments%2Fst-nerf%2Fboxing.zip"
curl -c "$cookie" -b "$cookie" -L -o data/taekwondo.zip \
  "${base}%2Fpersonal%2Fxliufe_connect_ust_hk%2FDocuments%2Fst-nerf%2Ftaekwondo.zip"
curl -c "$cookie" -b "$cookie" -L -o data/walking.zip \
  "${base}%2Fpersonal%2Fxliufe_connect_ust_hk%2FDocuments%2Fst-nerf%2Fwalking.zip"
rm -f "$cookie"
```

Remove only the scene directories these archives will replace, then hardlink
each zip into its scene directory. The conversion command finds that one zip
and extracts `pose/` plus `frame*/images`. Point clouds, labels, and background
meshes stay in the zip. `boxing.zip` has no `pose/`, so it is only linked:

```bash
rm -rf data/boxing data/taekwondo data/walking
mkdir -p data/boxing data/taekwondo data/walking
ln data/boxing.zip data/boxing/boxing.zip
ln data/taekwondo.zip data/taekwondo/taekwondo.zip
ln data/walking.zip data/walking/walking.zip
```

`boxing` has frames `frame1` through `frame71` and cameras `0` through `14`.
`taekwondo` has frames `frame1` through `frame101` and cameras `0` through `14`.
`walking` has frames `frame1` through `frame75` and cameras `0` through `15`.

Write COLMAP text models from the released poses:

```bash
python -m nvs2colmap.stnerf --path data/taekwondo --n-frames 101
python -m nvs2colmap.stnerf --path data/walking --n-frames 75
```

## Dataset Format

`walking` and `taekwondo` keep one shared pose directory and one folder per
frame. `walking` also stores a textured background mesh:

```text
walking/
  pose/
    K.txt
    RT_c2w.txt
  background/
    0.ply
    textured.obj
    textured.mtl
    textured.png
  frame1/
    images/
      0.png
      1.png
      ...
    labels/
      0.npy
      1.npy
      ...
    pointclouds/
      1.ply
      2.ply
  frame2/
    ...
```

`taekwondo/` has the same layout, with `background/0.ply` and no textured mesh.
`boxing/` has the same frame folders and `background/0.ply`, and no `pose/`.

`pose/K.txt` has one camera per line. Each line is nine floats, a row-major
3 x 3 intrinsic matrix. Line order is the camera index, so line 0 belongs to
`images/0.png`.

`pose/RT_c2w.txt` has one camera per line. Each line is twelve floats, a
row-major 3 x 4 camera-to-world matrix. The
[ST-NeRF loader](https://github.com/DarlingHang/ST-NeRF/blob/main/data/datasets/utils.py)
appends `[0, 0, 0, 1]` and reads that matrix as camera-to-world. Line order
matches `K.txt`.

Images are `1920 x 1080`. A label is a NumPy `uint8` array of shape
`(1080, 1920)`, one file per camera. `background/0.ply` is the background
layer. `pointclouds/1.ply` and `pointclouds/2.ply` are the two foreground
layers for that frame.

The official demo configs use a subset of these frames. `config_walking.yml`
sets `FRAME_OFFSET: 25` and `FRAME_NUM: 50`, so it reads `frame26` through
`frame75`. `config_taekwondo.yml` sets `FRAME_OFFSET: 0` and `FRAME_NUM: 101`,
so it reads `frame1` through `frame101`.

## Output Format

In the default mode, the command extracts images to `frame*/images` and adds
one COLMAP text model per frame:

```text
walking/
  frame1/
    images/
      0.png
      1.png
      ...
    sparse/0/
      cameras.txt
      images.txt
      points3D.txt
  frame2/
    ...
```

Image names in the COLMAP files are the source filenames, `0.png`, `1.png`,
and so on. `points3D.txt` is empty. The quick start leaves labels, point
clouds, and background meshes inside the zip.

With `--use-colmap`, images are extracted to `frame*/input`. COLMAP then
writes undistorted images to `images/`, plus `distorted/sparse/0`, `sparse/`,
`sparse/0`, and `stereo/`.

```text
walking/
  frame1/
    input/
      0.png
      1.png
      ...
    distorted/
      database.db
      sparse/0/
    images/
    sparse/
      0/
    stereo/
```

All generated camera models use `PINHOLE`. Every camera gets its own COLMAP
camera ID because these scenes are multi-view captures with known poses and
per-view intrinsics.

## Usage

Write COLMAP text models for an extracted scene:

```bash
python -m nvs2colmap.stnerf \
  --path data/taekwondo \
  --n-frames 101
```

Use the walking frames from the official demo config:

```bash
python -m nvs2colmap.stnerf \
  --path data/walking \
  --start-number 26 \
  --n-frames 50
```

Run the full COLMAP pipeline for each frame:

```bash
python -m nvs2colmap.stnerf \
  --path data/taekwondo \
  --n-frames 101 \
  --use-colmap \
  --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" \
  --colmap-use-gpu 1
```

## Important Options

- `--path`: scene directory containing one zip file.
- `--n-frames`: number of frames to extract and write after `--frame-skip`.
  If omitted, every kept frame from `--start-number` through the last frame
  in the zip is used. A value past the frames that remain writes those frames.
- `--start-number`: 1-based source frame to start from, default `1`. `frame1`
  in the zip is source frame 1. Output folders are renumbered from `frame1`.
- `--frame-skip`: keep every Nth source frame after `--start-number`, default
  `1`. Output folders stay `frame1`, `frame2`, ...
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable used with
  `--use-colmap`.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.

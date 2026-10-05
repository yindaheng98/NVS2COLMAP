# NVS2COLMAP

Utilities for converting novel view synthesis datasets to COLMAP format.

## Supported Formats

- **Neural 3D Video Dataset**: scenes with `poses_bounds.npy` and one `mp4`
  file per camera. See `nvs2colmap/n3dv/README.md`.
- **Dynamic 3D Gaussians**: scenes with `train_meta.json`, `test_meta.json`,
  images in `ims/`, and masks in `seg/`. See `nvs2colmap/dynamic3dgs/README.md`.

## Supported Datasets

- **Neural 3D Video Dataset**: dataset
  [facebookresearch/Neural_3D_Video](https://github.com/facebookresearch/Neural_3D_Video),
  paper
  [Neural 3D Video Synthesis from Multi-view Video](https://arxiv.org/abs/2103.02597).
- **StreamRF / Meet Room Dataset**: dataset
  [AlgoHunt/StreamRF](https://github.com/AlgoHunt/StreamRF), paper
  [Streaming Radiance Fields for 3D Video Synthesis](https://arxiv.org/abs/2210.14831).
- **Robo360**: dataset
  [liuyubian/Robo360](https://huggingface.co/datasets/liuyubian/Robo360),
  paper
  [Robo360: A 3D Omnispective Multi-Material Robotic Manipulation Dataset](https://arxiv.org/abs/2312.06686).
- **Dynamic 3D Gaussians**: dataset
  [JonathonLuiten/Dynamic3DGaussians](https://github.com/JonathonLuiten/Dynamic3DGaussians),
  paper
  [Dynamic 3D Gaussians: Tracking by Persistent Dynamic View Synthesis](https://arxiv.org/abs/2308.09713).

## Quick Start

Install the Python runtime dependencies:

```bash
pip install numpy torch
```

For Neural 3D Video scenes, the command also needs `ffmpeg` and `ffprobe` on
`PATH`, or explicit paths via `--ffmpeg` and `--ffprobe`. If you want to run
the full COLMAP pipeline, also provide a COLMAP executable via
`--colmap-executable`.

Extract a Neural 3D Video scene and write per-frame COLMAP text models:

```bash
python -m nvs2colmap.n3dv \
  --path data/coffee_martini \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --n-frames 300
```

Start from source frame 10 and keep output frame numbering aligned with it:

```bash
python -m nvs2colmap.n3dv \
  --path data/coffee_martini \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --start-number 10 \
  --n-frames 300
```

Run the full COLMAP pipeline for each frame:

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/xarm6_gold_rope_in_basket_2 \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --video-extension MP4 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable colmap \
  --colmap-use-gpu 1
```

Link a Dynamic 3D Gaussians scene, including its masks, and write per-frame
COLMAP text models:

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --n-frames 150
```

For Neural 3D Video scenes, decoded frames are written to `frame*/images` by
default, and the command also writes `frame*/sparse/0` text models. With
`--use-colmap`, decoded frames are written to `frame*/input`, and each frame
additionally gets the standard COLMAP outputs such as `distorted/`, `images/`,
`sparse/`, and `stereo/`. When `--start-number N` is provided, decoding starts
from source video frame `N`, and the generated folders/images are also numbered
from `N`.

For Dynamic 3D Gaussians scenes, images from both `train_meta.json` and
`test_meta.json` are hardlinked into `frame*/images`, and included masks are
hardlinked into `frame*/image_masks` (`cam01.jpg` pairs with `cam01.jpg.png`).
`--no-train-camera` and `--no-test-camera` drop one split. The same
`--use-colmap` switch writes images to `frame*/input` and runs COLMAP.
`--start-number` uses the same 1-based output numbering; source file
`000000.jpg` is frame `1`.
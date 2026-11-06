# NVS2COLMAP

Utilities for converting novel view synthesis datasets to COLMAP format.

**These scenes are prepared for [InstantSplat](https://github.com/yindaheng98/InstantSplat). InstantSplat initializes one frame at a time and does not undistort a whole sequence, so this repository undistorts every frame. The default commands write known-pose `sparse/0` text models and do not call COLMAP. `--use-colmap` runs feature extraction, matching, triangulation, mapping, `image_undistorter`, and `mask_undistorter` on every frame. Undistorted images go to `images/`, and undistorted masks go to `image_masks/`.**

## Supported Formats

- **Neural 3D Video Dataset**: scenes with `poses_bounds.npy` and one `mp4`
  file per camera. See `nvs2colmap/n3dv/README.md`.
- **Dynamic 3D Gaussians**: scenes with `train_meta.json`, `test_meta.json`,
  images in `ims/`, and masks in `seg/`. See `nvs2colmap/dynamic3dgs/README.md`.
- **Blender**: a `.blend` file rendered into that Neural 3D Video layout, with
  `blender_frames.json` recording the Blender timeline frame of each video
  frame. See `nvs2colmap/blender/README.md`.
- **ST-NeRF**: scenes with `pose/K.txt`, `pose/RT_c2w.txt`, and one
  `frame*/images` folder per frame. The released `boxing` archive has no
  `pose/`. See `nvs2colmap/stnerf/README.md`.
- **Siggraph Asia 2026 VVC**: scenes with `images/<view>/<frame>`,
  `train_intri.yml`, and `train_extri.yml`. See
  `nvs2colmap/SiggraphAsia2026VVC/README.md`.

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
- **ST-NeRF**: code
  [DarlingHang/ST-NeRF](https://github.com/DarlingHang/ST-NeRF),
  paper
  [Editable Free-Viewpoint Video using a Layered Neural Representation](https://arxiv.org/abs/2104.14786).
- **Siggraph Asia 2026 VVC**: dataset
  [zju3dv/SiggraphAsia2026VVC](https://huggingface.co/datasets/zju3dv/SiggraphAsia2026VVC).

## Quick Start

Install the Python runtime dependencies:

```bash
pip install numpy pillow plyfile torch
```

Download FFmpeg 7.0.2-static and place `ffmpeg` and `ffprobe` in `data/`:

```bash
mkdir -p data
wget -qO- https://johnvansickle.com/ffmpeg/releases/ffmpeg-7.0.2-amd64-static.tar.xz | tar -xJ -C data --strip-components=1 ffmpeg-7.0.2-amd64-static/ffmpeg ffmpeg-7.0.2-amd64-static/ffprobe
```

Install COLMAP from conda-forge:

```bash
conda install -c conda-forge colmap
```

The `colmap` executable is `${CONDA_EXE%/bin/conda}/bin/colmap`. It loads
shared libraries from the conda `lib` directory next to that binary, so pass
this path to `--colmap-executable`.

`--use-colmap` hardcodes the COLMAP 3.13 option names
`--FeatureExtraction.use_gpu` and `--FeatureMatching.use_gpu`. COLMAP 3.12 and
earlier only accept `--SiftExtraction.use_gpu` and `--SiftMatching.use_gpu`,
and exit with `unrecognised option '--SiftExtraction.use_gpu'`. Install COLMAP
3.13 or newer.

For Neural 3D Video scenes, pass `data/ffmpeg` and `data/ffprobe`, or put
`ffmpeg` and `ffprobe` on `PATH`. To run the COLMAP reconstruction that
[InstantSplat](https://github.com/yindaheng98/InstantSplat) continues from,
pass `--colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"`.

Extract a Neural 3D Video scene and write per-frame COLMAP text models for
[InstantSplat](https://github.com/yindaheng98/InstantSplat):

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

Run COLMAP reconstruction and undistortion for each frame, for
[InstantSplat](https://github.com/yindaheng98/InstantSplat):

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/xarm6_gold_rope_in_basket_2 \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --video-extension MP4 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" \
  --colmap-use-gpu 1
```

Link a Dynamic 3D Gaussians scene, including its masks, and write per-frame
COLMAP text models for
[InstantSplat](https://github.com/yindaheng98/InstantSplat):

```bash
python -m nvs2colmap.dynamic3dgs \
  --path data/basketball \
  --n-frames 150
```

Write per-frame COLMAP text models for an ST-NeRF scene. The scene must
contain `pose/K.txt` and `pose/RT_c2w.txt`:

```bash
python -m nvs2colmap.stnerf \
  --path data/taekwondo \
  --n-frames 101
```

Link a Siggraph Asia 2026 VVC scene and write per-frame COLMAP text models
for [InstantSplat](https://github.com/yindaheng98/InstantSplat). The default
starts at the first frame file and writes `frame1`, including a `selfcap`
scene whose first file is `000900.jpg`:

```bash
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/siga/compression/test/004_1_seq1
python -m nvs2colmap.SiggraphAsia2026VVC \
  --path data/SiggraphAsia2026VVC/selfcap/sparse/test/0512_bike
```

Render a `.blend` file into camera videos next to an existing
`poses_bounds.npy`. `blender` must be on `PATH`, or pass the executable with
`--blender`:

```bash
python -m nvs2colmap.blender \
  --path data/robot \
  --blend robot.blend \
  --frame_step 3
```

For Neural 3D Video scenes, decoded frames are written to `frame*/images` by
default, and the command also writes `frame*/sparse/0` text models. With
`--use-colmap`, decoded frames are written to `frame*/input`, and each frame
gets `distorted/sparse/0` plus undistorted `images/`, `sparse/`, and `stereo/`
for [InstantSplat](https://github.com/yindaheng98/InstantSplat). When
`--start-number N` is provided, decoding starts from source video frame `N`,
and the generated folders/images are also numbered from `N`.

For Dynamic 3D Gaussians scenes, images from both `train_meta.json` and
`test_meta.json` are hardlinked into `frame*/images`, and included masks are
hardlinked into `frame*/image_masks` (`cam01.jpg` pairs with `cam01.jpg.png`).
`--no-train-camera` and `--no-test-camera` drop one split. The same
`--use-colmap` switch writes images to `frame*/input` and masks to
`frame*/input_mask`, then undistorts them to `images/` and `image_masks/`
for [InstantSplat](https://github.com/yindaheng98/InstantSplat). That switch
does not write `init_pt_cld.npz` into `sparse/0/points3D.ply`; the
reconstructed points stay in `distorted/sparse/0` and the undistorted
`sparse/`. `--start-number` uses the same 1-based output numbering; source
file `000000.jpg` is frame `1`.

For Siggraph Asia 2026 VVC scenes, images from `train_intri.yml` /
`train_extri.yml` and, when present, `test_intri.yml` / `test_extri.yml` are
placed in `frame*/images`. Included masks go in `frame*/image_masks`
(`0002.jpg` pairs with `0002.jpg.png`). A zero `D_<view>` is hardlinked. A
nonzero `D_<view>` hardlinks the original into `frame*/input`. COLMAP's
`image_undistorter` writes `frame*/images` and a `PINHOLE` model in
`sparse/0`. A shared `pcds/000000.ply` is hardlinked to `sparse/0/points3D.ply`
in every extracted frame. `--use-colmap` writes images to `frame*/input` and
masks to `frame*/input_mask`, then runs COLMAP undistortion into `images/` and
`image_masks/` for
[InstantSplat](https://github.com/yindaheng98/InstantSplat). The default
starts at the first frame file and writes `frame1`. A scene whose first file
is `000900.jpg` still begins at `frame1`.

For Blender scenes, rendering writes one video per camera beside
`poses_bounds.npy`, plus `blender_frames.json` in that same directory. The
file is a JSON list of Blender timeline frame numbers in render order. Video
frame `i` (1-based) is Blender frame `blender_frames[i - 1]`.
`--frame_start` defaults to `1`. `--frame_end` and `--frame_step` default to
the `.blend` timeline. With `--frame_step 3`, the file begins `[1, 4, 7, ...]`.
Decoding the videos with `python -m nvs2colmap.n3dv` numbers `frame*` folders
by video frame, so `frameK` is `blender_frames[K - 1]`.

For ST-NeRF scenes, the scene directory holds one zip file. The default
command extracts images to `frame*/images` and writes `frame*/sparse/0` text
models from `pose/K.txt` and `pose/RT_c2w.txt`. `--use-colmap` extracts images
to `frame*/input`, then undistorts them to `images/` for
[InstantSplat](https://github.com/yindaheng98/InstantSplat). A scene without
`pose/` raises an error. `--start-number` uses the same 1-based numbering;
source directory `frame1` is frame `1`.
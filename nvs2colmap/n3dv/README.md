# Neural 3D Video Dataset

This package converts scenes in the **Neural 3D Video Dataset** format into
per-frame COLMAP outputs. By default it writes COLMAP text models. With
`--use-colmap`, it runs the full COLMAP pipeline on every extracted frame.

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

Runtime dependencies:

```bash
pip install numpy torch
```

The command also needs `ffmpeg` and `ffprobe` on `PATH`, or explicit paths via
`--ffmpeg` and `--ffprobe`.

## Dataset Format

A scene folder is expected to contain one `poses_bounds.npy` file plus one
video per camera:

```text
coffee_martini/
  poses_bounds.npy
  cam00.mp4
  cam01.mp4
  cam02.mp4
  ...
```

`poses_bounds.npy` follows the LLFF-style `poses_bounds` layout:

- Shape: `(num_cameras, 17)`.
- The first 15 values in each row reshape to a `3 x 5` matrix.
- The first `3 x 4` block stores the camera-to-world pose in the dataset's
  LLFF axis convention.
- The last column stores `height`, `width`, and focal length.
- The final 2 values store near/far bounds; this converter keeps the camera
  pose and intrinsics and does not write bounds into COLMAP files.

Videos are read by suffix, default `.mp4`, and sorted by filename. The sorted
videos are matched against `poses_bounds.npy` rows in that order. Output image
names and COLMAP image names use the corresponding video filename stems.
By default, extraction starts from source frame `1`, producing `frame1`,
`frame2`, ... . Passing `--start-number N` starts decoding from source video
frame `N` and also numbers output folders and image files from `N`.

## Output Format

In the default mode, the command decodes one image per camera into
`frame*/images`:

```text
coffee_martini/
  frame1/
    images/
      cam00.png
      cam01.png
      ...
  frame2/
    images/
  ...
```

In the default mode, it also writes one COLMAP text model per frame:

```text
coffee_martini/
  frame1/
    sparse/0/
      cameras.txt
      images.txt
      points3D.txt
  frame2/
    sparse/0/
  ...
```

With `--use-colmap`, each frame directory instead contains the usual COLMAP
workspace outputs after feature extraction, matching, triangulation, mapping,
and undistortion:

```text
coffee_martini/
  frame1/
    input/
    distorted/
      database.db
      sparse/0/
        cameras.bin
        images.bin
        points3D.bin
    images/
    sparse/
      cameras.bin
      images.bin
      points3D.bin
    stereo/
```

All generated camera models use `PINHOLE`. Every camera gets its own COLMAP
camera ID because Neural 3D Video scenes are multi-view captures with known
static poses and per-view intrinsics.

If the source videos are named `0001.MP4`, `0002.MP4`, etc., the images and
COLMAP records are named `0001.png`, `0002.png`, etc. Use `--video-extension
MP4` for uppercase video suffixes.

## Usage

Decode videos and write COLMAP text models for an extracted scene:

```bash
python -m nvs2colmap.n3dv \
  --path data/cook_spinach \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --n-frames 300
```

Start decoding from source frame 10:

```bash
python -m nvs2colmap.n3dv \
  --path data/cook_spinach \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --start-number 10 \
  --n-frames 300
```

Decode uppercase `.MP4` videos:

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/xarm6_gold_rope_in_basket_2 \
  --ffmpeg D:/MyPrograms/ffmpeg.exe \
  --ffprobe D:/MyPrograms/ffprobe.exe \
  --video-extension MP4 \
  --n-frames 1
```

Run the full COLMAP pipeline instead of only writing text models:

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/xarm6_gold_rope_in_basket_2 \
  --ffmpeg D:/MyPrograms/ffmpeg.exe \
  --ffprobe D:/MyPrograms/ffprobe.exe \
  --video-extension MP4 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable data/colmap/COLMAP.bat \
  --colmap-use-gpu 1
```

Reuse existing extracted frame images:

```bash
python -m nvs2colmap.n3dv \
  --path data/coffee_martini \
  --skip-video-extraction
```

## Important Options

- `--path`: scene directory containing `poses_bounds.npy` and camera videos.
- `--n-frames`: number of frames to extract and write. If omitted while
  extracting videos, each video is decoded to its available frame count. For
  best results, use videos with matching frame counts or pass `--n-frames`.
  If omitted with `--skip-video-extraction`, frame directories are counted
  from `frame%d`.
- `--start-number`: 1-based source frame index to start decoding from, default
  `1`. Output `frame%d` folders and written image filenames use the same
  numbering start.
- `--ffmpeg`: path to the `ffmpeg` executable.
- `--ffprobe`: path to the `ffprobe` executable.
- `--image-extension`: image extension written by ffmpeg and referenced by
  COLMAP files, default `.png`.
- `--video-extension`: video file extension to read, default `.mp4`. The dot is
  optional and matching is case-insensitive.
- `--skip-video-extraction`: keep existing extracted frame images and skip video
  decoding. In the default mode this reuses `frame*/images`; with
  `--use-colmap` it reuses `frame*/input`. If `--n-frames` is omitted, the
  command counts existing `frame%d` directories.
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable used with
  `--use-colmap`.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.
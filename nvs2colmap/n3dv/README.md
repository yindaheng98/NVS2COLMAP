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

## Quick Start - Neural 3D Video

Each official archive contains one scene directory. Overwrite the zip files in
`data/` if they already exist. Those files stay as downloaded.
`flame_salmon_1` is published as the split archive `flame_salmon_1_split.zip`
plus `flame_salmon_1_split.z01` through `flame_salmon_1_split.z03`:

```bash
mkdir -p data
wget -O data/coffee_martini.zip https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/coffee_martini.zip
wget -O data/cook_spinach.zip https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/cook_spinach.zip
wget -O data/cut_roasted_beef.zip https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/cut_roasted_beef.zip
wget -O data/flame_steak.zip https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/flame_steak.zip
wget -O data/sear_steak.zip https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/sear_steak.zip
wget -O data/flame_salmon_1_split.zip https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/flame_salmon_1_split.zip
wget -O data/flame_salmon_1_split.z01 https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/flame_salmon_1_split.z01
wget -O data/flame_salmon_1_split.z02 https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/flame_salmon_1_split.z02
wget -O data/flame_salmon_1_split.z03 https://github.com/facebookresearch/Neural_3D_Video/releases/download/v1.0/flame_salmon_1_split.z03
```

Remove only the scenes these archives will replace. `zip -F` rebuilds
`data/flame_salmon_1.zip` from the split archive, then extract with `-d data`
so the scenes land at `data/coffee_martini`, `data/cook_spinach`, and the
other sequence folders:

```bash
rm -rf data/coffee_martini data/cook_spinach data/cut_roasted_beef data/flame_salmon_1 data/flame_steak data/sear_steak
(
  cd data
  zip -F flame_salmon_1_split.zip --out flame_salmon_1.zip
)
unzip -d data data/coffee_martini.zip
unzip -d data data/cook_spinach.zip
unzip -d data data/cut_roasted_beef.zip
unzip -d data data/flame_steak.zip
unzip -d data data/sear_steak.zip
unzip -d data data/flame_salmon_1.zip
```

Decode the videos and write COLMAP text models. Each scene is one command:

```bash
python -m nvs2colmap.n3dv --path data/coffee_martini --n-frames 300
python -m nvs2colmap.n3dv --path data/cook_spinach --n-frames 300
python -m nvs2colmap.n3dv --path data/cut_roasted_beef --n-frames 300
python -m nvs2colmap.n3dv --path data/flame_salmon_1 --n-frames 1200
python -m nvs2colmap.n3dv --path data/flame_steak --n-frames 300
python -m nvs2colmap.n3dv --path data/sear_steak --n-frames 300
```

## Quick Start - StreamRF

The Meet Room release is four zip archives on ModelScope,
[DAMOXR/dynamic_nerf_meeting_room_dataset](https://www.modelscope.cn/datasets/DAMOXR/dynamic_nerf_meeting_room_dataset):
`discussion.zip`, `trimming.zip`, `stepin.zip`, and `vrheadset.zip`, about
1.1 GB together. Each archive contains one scene directory. ModelScope asks
for an SDK token from the
[access-token page](https://modelscope.cn/my/myaccesstoken). Overwrite the zip
files in `data/` if they already exist. Those zip files stay as downloaded.

The StreamRF README also links a
[Google Drive folder](https://drive.google.com/drive/folders/1lNmQ6_ykyKjT6UKy-SnqWoSlI5yjh3l_).
Its `MeetRoom` directory stores `discussion`, `trimming`, and `vrheadset` as
loose `cam_*.mp4` files plus `poses_bounds.npy`. `stepin` is in the ModelScope
archives above.

```bash
pip install modelscope
modelscope login --token <SDK token>
mkdir -p data
modelscope download --dataset DAMOXR/dynamic_nerf_meeting_room_dataset \
  discussion.zip trimming.zip stepin.zip vrheadset.zip \
  --local_dir data
```

Remove only the scenes these archives will replace, then extract with
`-d data`:

```bash
rm -rf data/discussion data/trimming data/stepin data/vrheadset
unzip -d data data/discussion.zip
unzip -d data data/trimming.zip
unzip -d data data/stepin.zip
unzip -d data data/vrheadset.zip
```

Each scene has `poses_bounds.npy` and `cam_0.mp4` through `cam_12.mp4`. Every
video is 10 seconds at 30 fps, so each sequence is 300 frames.

Decode the videos and write COLMAP text models. Each scene is one command:

```bash
python -m nvs2colmap.n3dv --path data/discussion --n-frames 300
python -m nvs2colmap.n3dv --path data/trimming --n-frames 300
python -m nvs2colmap.n3dv --path data/stepin --n-frames 300
python -m nvs2colmap.n3dv --path data/vrheadset --n-frames 300
```

## Quick Start - Robo360

The release is the Hugging Face dataset
[liuyubian/Robo360](https://huggingface.co/datasets/liuyubian/Robo360), about
47.3 GB. Scenes are already unpacked. `batch1` has 28 scenes and `batch2` has 15. A scene directory contains `poses_bounds.npy` and one video per camera,
named `0001.mp4`, `0002.mp4`, and so on. `batch1` videos use a lowercase
`.mp4` suffix. `batch2` videos use `.MP4`, so those commands pass
`--video-extension MP4`. Camera counts differ by scene. Some scenes also
include `begin_length_same.txt` or a `traj/` directory; conversion reads
`poses_bounds.npy` and the camera videos.

```bash
pip install -U huggingface_hub
mkdir -p data/Robo360
hf download liuyubian/Robo360 \
  --type dataset \
  --local-dir data/Robo360
```

Videos in one scene can differ in length, so these commands decode each
video to its available frame count. Each scene is one command:

```bash
python -m nvs2colmap.n3dv --path data/Robo360/batch1/bread_fall
python -m nvs2colmap.n3dv --path data/Robo360/batch1/bread_tear
python -m nvs2colmap.n3dv --path data/Robo360/batch1/cable_aug25_1500
python -m nvs2colmap.n3dv --path data/Robo360/batch1/captain
python -m nvs2colmap.n3dv --path data/Robo360/batch1/carrot_break
python -m nvs2colmap.n3dv --path data/Robo360/batch1/carrot_fall
python -m nvs2colmap.n3dv --path data/Robo360/batch1/carrot_push
python -m nvs2colmap.n3dv --path data/Robo360/batch1/cloth
python -m nvs2colmap.n3dv --path data/Robo360/batch1/coffeepour
python -m nvs2colmap.n3dv --path data/Robo360/batch1/cucumber_break
python -m nvs2colmap.n3dv --path data/Robo360/batch1/cucumber_fall
python -m nvs2colmap.n3dv --path data/Robo360/batch1/cucumber_push
python -m nvs2colmap.n3dv --path data/Robo360/batch1/flashdriveinsert
python -m nvs2colmap.n3dv --path data/Robo360/batch1/lettuce_break
python -m nvs2colmap.n3dv --path data/Robo360/batch1/lettuce_push
python -m nvs2colmap.n3dv --path data/Robo360/batch1/lunchbox
python -m nvs2colmap.n3dv --path data/Robo360/batch1/peginsert
python -m nvs2colmap.n3dv --path data/Robo360/batch1/plasticine_ball_fall
python -m nvs2colmap.n3dv --path data/Robo360/batch1/plasticine_rope_fall
python -m nvs2colmap.n3dv --path data/Robo360/batch1/plasticine_rope_push
python -m nvs2colmap.n3dv --path data/Robo360/batch1/rope_pick
python -m nvs2colmap.n3dv --path data/Robo360/batch1/rope_tie_knot
python -m nvs2colmap.n3dv --path data/Robo360/batch1/sand
python -m nvs2colmap.n3dv --path data/Robo360/batch1/tong
python -m nvs2colmap.n3dv --path data/Robo360/batch1/xarm6_captain_pick_rotate
python -m nvs2colmap.n3dv --path data/Robo360/batch1/xarm6_hammer_down_peg
python -m nvs2colmap.n3dv --path data/Robo360/batch1/xarm6_peg_insertion
python -m nvs2colmap.n3dv --path data/Robo360/batch1/xarm6_put_fork_in_mug
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_bottle_flip_fast --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_bread_fall --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_cucumber_skewer --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_dish_soap --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_fold_tshirt --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_fortune_cookie --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_gold_rope_in_basket_2 --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_plastic_air_bag --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_plugboard --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_pour_orange_juice_2 --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_put_bread_in_plastic_bag --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_sand_pour --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_sprite_pour_2 --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_sprite_stack --video-extension MP4
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_unfold_tshirt --video-extension MP4
```

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
frame `N` and renumbers the extracted frames from `frame1`.

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

With `--use-colmap`, each frame directory instead contains the COLMAP workspace
after feature extraction, matching, triangulation, mapping, and undistortion.
`image_undistorter` writes `images/`, `sparse/`, and `stereo/`. The same
undistorted model is also written as text to `sparse/0`.

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
      0/
        cameras.txt
        images.txt
        points3D.txt
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
  --path data/Robo360/batch2/xarm6_gold_rope_in_basket_2 \
  --ffmpeg D:/MyPrograms/ffmpeg.exe \
  --ffprobe D:/MyPrograms/ffprobe.exe \
  --video-extension MP4 \
  --n-frames 1
```

Run the full COLMAP pipeline instead of only writing text models:

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/batch2/xarm6_gold_rope_in_basket_2 \
  --ffmpeg D:/MyPrograms/ffmpeg.exe \
  --ffprobe D:/MyPrograms/ffprobe.exe \
  --video-extension MP4 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" \
  --colmap-use-gpu 1
```

## Important Options

- `--path`: scene directory containing `poses_bounds.npy` and camera videos.
- `--n-frames`: number of frames to extract and write. If omitted, each video
  is decoded to its available frame count. For best results, use videos with
  matching frame counts or pass `--n-frames`.
- `--start-number`: 1-based source frame index to start decoding from, default
  `1`. Output `frame%d` folders are renumbered from `frame1`.
- `--frame-skip`: keep every Nth source frame after `--start-number`, default
  `1`. Output folders stay contiguous from `frame1`.
- `--ffmpeg`: path to the `ffmpeg` executable.
- `--ffprobe`: path to the `ffprobe` executable.
- `--image-extension`: image extension written by ffmpeg and referenced by
  COLMAP files, default `.png`.
- `--video-extension`: video file extension to read, default `.mp4`. The dot is
  optional and matching is case-insensitive.
- `--use-colmap`: run the full COLMAP pipeline instead of only writing
  `sparse/0` text models.
- `--colmap-executable`: path to the COLMAP executable used with
  `--use-colmap`.
- `--colmap-use-gpu`: whether COLMAP SIFT extraction and matching should use
  GPU, default `1`.

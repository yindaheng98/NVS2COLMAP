#!/bin/bash
set -e
./nvs2colmap/n3dv/reset_n3dv.sh --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"
./nvs2colmap/dynamic3dgs/reset_dynamic3dgs.sh --use-colmap --refine-init-pose --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"
./nvs2colmap/n3dv/reset_Robo360batch1.sh --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" --n-frames 300
./nvs2colmap/n3dv/reset_Robo360batch2.sh --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" --frame-skip 6 --n-frames 300
./nvs2colmap/SiggraphAsia2026VVC/reset_SiggraphAsia2026VVC_selfcap.sh --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" --frame-skip 3 --n-frames 300
./nvs2colmap/SiggraphAsia2026VVC/reset_SiggraphAsia2026VVC_siga.sh --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap" --frame-skip 2 --n-frames 300

reset_streamrf() {
    rm -rf data/discussion data/trimming data/stepin data/vrheadset
    unzip -d data data/discussion.zip
    unzip -d data data/trimming.zip
    unzip -d data data/stepin.zip
    unzip -d data data/vrheadset.zip
    # streamrf camera poses are not good, so we use the camera poses from the first frame
    CAMERAS_DIR="data/saved_frame1/data"
    python -m nvs2colmap.n3dv --path data/discussion --cameras $CAMERAS_DIR/discussion/frame1/sparse/0 "$@"
    python -m nvs2colmap.n3dv --path data/trimming --cameras $CAMERAS_DIR/trimming/frame1/sparse/0 "$@"
    python -m nvs2colmap.n3dv --path data/stepin --cameras $CAMERAS_DIR/stepin/frame1/sparse/0 "$@"
    python -m nvs2colmap.n3dv --path data/vrheadset --cameras $CAMERAS_DIR/vrheadset/frame1/sparse/0 "$@"
}
reset_streamrf --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"

#!/bin/bash
set -e
./nvs2colmap/n3dv/reset_n3dv.sh --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"
./nvs2colmap/dynamic3dgs/reset_dynamic3dgs.sh --use-colmap --refine-poses --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"
./nvs2colmap/n3dv/reset_streamrf.sh --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --refine-poses --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"
./nvs2colmap/n3dv/reset_robo360.sh --ffmpeg data/ffmpeg --ffprobe data/ffprobe --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"
./nvs2colmap/SiggraphAsia2026VVC/reset_SiggraphAsia2026VVC.sh --use-colmap --colmap-executable "${CONDA_EXE%/bin/conda}/bin/colmap"

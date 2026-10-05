"""Render one video per camera. Executed by Blender, not by the project interpreter."""

import argparse
import json
import sys
from pathlib import Path

import bpy
import mathutils


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cameras", type=json.loads, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

    scene = bpy.context.scene
    cam_obj = scene.camera
    cam_obj.animation_data_clear()
    cam = cam_obj.data
    cam.sensor_fit = "HORIZONTAL"
    cam.sensor_width = 36.0
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.audio_codec = "NONE"
    scene.render.use_file_extension = False

    for name, height, width, focal, c2w in args.cameras:
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        cam.lens = focal * cam.sensor_width / width
        cam_obj.matrix_world = mathutils.Matrix(c2w)
        scene.render.filepath = str(args.output / f"{name}.mp4")
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()

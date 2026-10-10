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
    parser.add_argument("--start-number", type=int, default=1)
    parser.add_argument("--n-frames", type=int)
    parser.add_argument("--frame-step", type=int, default=1)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

    scene = bpy.context.scene
    cam_obj = scene.camera
    cam_obj.animation_data_clear()
    cam = cam_obj.data
    cam.sensor_fit = "HORIZONTAL"
    cam.sensor_width = 36.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.eevee.use_raytracing = False
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.audio_codec = "NONE"
    scene.render.use_file_extension = False
    scene.frame_start += args.start_number - 1
    if args.n_frames is not None:
        scene.frame_end = min(scene.frame_end, scene.frame_start + args.n_frames - 1)
    scene.frame_step = args.frame_step
    scene.render.fps_base *= args.frame_step
    # Video frame i (1-based) is this Blender frame.
    frames = list(range(scene.frame_start, scene.frame_end + 1, scene.frame_step))
    (args.output / "blender_frames.json").write_text(json.dumps(frames) + "\n")

    for name, height, width, focal, c2w in args.cameras:
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        cam.lens = focal * cam.sensor_width / width
        cam_obj.matrix_world = mathutils.Matrix(c2w)
        scene.render.filepath = str(args.output / f"{name}.mp4")
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()

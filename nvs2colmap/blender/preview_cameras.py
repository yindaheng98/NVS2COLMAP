"""Place sampled cameras in the open Blender file. Executed by Blender."""

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
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])

    scene = bpy.context.scene
    collection = bpy.data.collections.new("cameras")
    scene.collection.children.link(collection)
    for name, height, width, focal, c2w in args.cameras:
        camera = bpy.data.cameras.new(name)
        camera.sensor_fit = "HORIZONTAL"
        camera.sensor_width = 36.0
        camera.lens = focal * camera.sensor_width / width
        camera.clip_start = 0.1
        camera.clip_end = 30.0
        camera.display_size = 2.0
        obj = bpy.data.objects.new(name, camera)
        obj.show_name = True
        obj.matrix_world = mathutils.Matrix(c2w)
        collection.objects.link(obj)
        scene.camera = obj
        scene.render.resolution_x = width
        scene.render.resolution_y = height
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))
    print(f"Done: {args.output}")


if __name__ == "__main__":
    main()

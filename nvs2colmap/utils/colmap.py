"""COLMAP command helpers."""

import sqlite3
import subprocess
import os


def execute(cmd):
    proc = subprocess.Popen(cmd, shell=False)
    proc.communicate()
    return proc.returncode


def feature_extractor(args, folder):
    os.makedirs(os.path.join(folder, "distorted"), exist_ok=True)
    cmd = [
        args.colmap_executable, "feature_extractor",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--image_path", os.path.join(folder, "input"),
        "--ImageReader.camera_model", "PINHOLE",
        "--SiftExtraction.use_gpu", args.use_gpu,
        "--ImageReader.single_camera_per_image", "1",
    ]
    return execute(cmd)


def exhaustive_matcher(args, folder):
    cmd = [
        args.colmap_executable, "exhaustive_matcher",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--SiftMatching.use_gpu", args.use_gpu,
    ]
    return execute(cmd)


def read_db(folder):
    conn = sqlite3.connect(os.path.join(folder, "distorted", "database.db"))
    c = conn.cursor()
    c.execute(f"SELECT camera_id,image_id,name FROM main.images")
    camera_ids, image_ids = {}, {}
    for camera_id, image_id, name in c.fetchall():
        camera_ids[name] = camera_id
        image_ids[name] = image_id
    conn.close()
    return camera_ids, image_ids


def point_triangulator(args, folder, mapper_input_path):
    cmd = [
        args.colmap_executable, "point_triangulator",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--input_path", mapper_input_path,
        "--output_path", mapper_input_path,
        "--image_path", os.path.join(folder, "input")
    ]
    return execute(cmd)


def mapper(args, folder, mapper_input_path):
    os.makedirs(os.path.join(folder, "distorted", "sparse", "0"), exist_ok=True)
    cmd = [
        args.colmap_executable, "mapper",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--image_path", os.path.join(folder, "input"),
        "--Mapper.ba_global_function_tolerance=0.000001",
        "--input_path", mapper_input_path,
        "--output_path", os.path.join(folder, "distorted", "sparse", "0")
    ]
    return execute(cmd)


def model_converter_txt(folder, colmap_executable):
    mapper_output_path = os.path.join(folder, "distorted", "sparse", "0")
    os.makedirs(mapper_output_path, exist_ok=True)
    cmd = [
        colmap_executable, "model_converter",
        "--input_path", mapper_output_path,
        "--output_path", mapper_output_path,
        "--output_type=TXT",
    ]
    return execute(cmd)


def model_converter_bin(folder, colmap_executable):
    mapper_output_path = os.path.join(folder, "distorted", "sparse", "0")
    os.makedirs(mapper_output_path, exist_ok=True)
    cmd = [
        colmap_executable, "model_converter",
        "--input_path", mapper_output_path,
        "--output_path", mapper_output_path,
        "--output_type=BIN",
    ]
    return execute(cmd)


def image_undistorter(args, folder):
    cmd = [
        args.colmap_executable, "image_undistorter",
        "--image_path", os.path.join(folder, "input"),
        "--input_path", os.path.join(folder, "distorted", "sparse", "0"),
        "--output_path", folder,
        "--output_type=COLMAP",
    ]
    return execute(cmd)

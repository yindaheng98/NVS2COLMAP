"""COLMAP command helpers."""

import filecmp
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path


def execute(cmd):
    proc = subprocess.Popen(cmd, shell=False)
    proc.communicate()
    return proc.returncode


def feature_extractor(folder, use_gpu="1", colmap_executable="colmap"):
    os.makedirs(os.path.join(folder, "distorted"), exist_ok=True)
    cmd = [
        colmap_executable, "feature_extractor",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--image_path", os.path.join(folder, "input"),
        "--ImageReader.camera_model", "PINHOLE",
        "--FeatureExtraction.use_gpu", use_gpu,
        "--ImageReader.single_camera_per_image", "1",
    ]
    feature_mask_dir = os.path.join(folder, "feature_mask")
    if os.path.isdir(feature_mask_dir):
        cmd += ["--ImageReader.mask_path", feature_mask_dir]
    return execute(cmd)


def exhaustive_matcher(folder, use_gpu="1", colmap_executable="colmap"):
    cmd = [
        colmap_executable, "exhaustive_matcher",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--FeatureMatching.use_gpu", use_gpu,
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


def point_triangulator(folder, mapper_input_path, colmap_executable="colmap"):
    cmd = [
        colmap_executable, "point_triangulator",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--input_path", mapper_input_path,
        "--output_path", mapper_input_path,
        "--image_path", os.path.join(folder, "input")
    ]
    return execute(cmd)


def bundle_adjuster(model_path, colmap_executable="colmap"):
    """Refine camera poses in an existing model. Intrinsics stay fixed.

    COLMAP 3.13 stores a legacy images.txt pose as rig_from_world on a
    one-camera rig, so only that transform is optimized. The reference
    sensor_from_rig stays identity.
    """
    cmd = [
        colmap_executable, "bundle_adjuster",
        "--input_path", model_path,
        "--output_path", model_path,
        "--BundleAdjustment.refine_focal_length", "0",
        "--BundleAdjustment.refine_principal_point", "0",
        "--BundleAdjustment.refine_extra_params", "0",
        "--BundleAdjustment.refine_rig_from_world", "1",
        "--BundleAdjustment.refine_sensor_from_rig", "0",
    ]
    return execute(cmd)


def mapper(folder, mapper_input_path, colmap_executable="colmap"):
    os.makedirs(os.path.join(folder, "distorted", "sparse", "0"), exist_ok=True)
    cmd = [
        colmap_executable, "mapper",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--image_path", os.path.join(folder, "input"),
        "--input_path", mapper_input_path,
        "--output_path", os.path.join(folder, "distorted", "sparse", "0")
    ]
    return execute(cmd)


def model_converter_txt(folder, colmap_executable="colmap"):
    mapper_output_path = os.path.join(folder, "distorted", "sparse", "0")
    os.makedirs(mapper_output_path, exist_ok=True)
    cmd = [
        colmap_executable, "model_converter",
        "--input_path", mapper_output_path,
        "--output_path", mapper_output_path,
        "--output_type=TXT",
    ]
    return execute(cmd)


def model_converter_bin(folder, colmap_executable="colmap"):
    mapper_output_path = os.path.join(folder, "distorted", "sparse", "0")
    os.makedirs(mapper_output_path, exist_ok=True)
    cmd = [
        colmap_executable, "model_converter",
        "--input_path", mapper_output_path,
        "--output_path", mapper_output_path,
        "--output_type=BIN",
    ]
    return execute(cmd)


def link_identical_files(source_dir, output_dir) -> None:
    """Replace output copies that match their source files with hardlinks."""
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    if not source_dir.is_dir() or not output_dir.is_dir():
        return
    for output in output_dir.rglob("*"):
        if not output.is_file():
            continue
        source = source_dir / output.relative_to(output_dir)
        if not source.is_file() or source.samefile(output):
            continue
        if not filecmp.cmp(source, output, shallow=False):
            continue
        temporary = output.with_name(output.name + ".linktmp")
        if temporary.exists():
            temporary.unlink()
        os.link(source, temporary)
        os.replace(temporary, output)


def image_undistorter(folder, colmap_executable="colmap"):
    shutil.rmtree(os.path.join(folder, "images"), ignore_errors=True)
    cmd = [
        colmap_executable, "image_undistorter",
        "--image_path", os.path.join(folder, "input"),
        "--input_path", os.path.join(folder, "distorted", "sparse", "0"),
        "--output_path", folder,
        "--output_type=COLMAP",
    ]
    return_code = execute(cmd)
    if return_code == 0:
        link_identical_files(Path(folder) / "input", Path(folder) / "images")
    return return_code


def mask_undistorter(folder, image_names, colmap_executable="colmap"):
    folder = Path(folder)
    image_names = [Path(name) for name in image_names]
    if not (folder / "input_mask").is_dir():
        return 0
    shutil.rmtree(folder / "tmp_mask", ignore_errors=True)
    exists = False
    for image_name in image_names:
        src = folder / "input_mask" / image_name.with_name(image_name.name + ".png")
        dst = folder / "tmp_mask" / image_name
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.link(src, dst)
        exists = True
    if not exists:
        shutil.rmtree(folder / "tmp_mask", ignore_errors=True)
        return 0
    shutil.rmtree(folder / "tmp_mask_sparse", ignore_errors=True)
    ret = execute([
        colmap_executable, "image_undistorter",
        "--image_path", os.fspath(folder / "tmp_mask"),
        "--input_path", os.fspath(folder / "distorted" / "sparse" / "0"),
        "--output_path", os.fspath(folder / "tmp_mask_sparse"),
        "--output_type=COLMAP",
    ])
    shutil.rmtree(folder / "tmp_mask", ignore_errors=True)
    if ret != 0:
        shutil.rmtree(folder / "tmp_mask_sparse", ignore_errors=True)
        return ret
    for image_name in image_names:
        src = folder / "tmp_mask_sparse" / "images" / image_name
        dst = folder / "image_masks" / image_name.with_name(image_name.name + ".png")
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        os.link(src, dst)
    link_identical_files(folder / "input_mask", folder / "image_masks")
    shutil.rmtree(folder / "tmp_mask_sparse", ignore_errors=True)
    return 0

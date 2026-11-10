"""COLMAP command helpers."""

import filecmp
import os
import shutil
import sqlite3
import struct
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
        "--image_path", os.path.join(folder, "input"),
        "--Mapper.ba_refine_focal_length", "0",
        "--Mapper.ba_refine_principal_point", "0",
        "--Mapper.ba_refine_extra_params", "0",
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


def write_camera_intrinsics(folder, intrinsics):
    """Store dataset PINHOLE intrinsics and mark the focal length as a prior.

    ``intrinsics`` maps an image name to ``(fx, fy, cx, cy)``. Each image has
    its own camera because extraction uses ``single_camera_per_image``.
    """
    conn = sqlite3.connect(os.path.join(folder, "distorted", "database.db"))
    c = conn.cursor()
    c.execute("SELECT camera_id, name FROM main.images")
    camera_ids = {name: camera_id for camera_id, name in c.fetchall()}
    missing = sorted(set(intrinsics) - set(camera_ids))
    if missing:
        conn.close()
        raise RuntimeError(f"Intrinsic images are missing from the database: {missing}")
    c.execute("SELECT camera_id, model FROM cameras")
    models = {camera_id: model for camera_id, model in c.fetchall()}
    # COLMAP's PINHOLE model id is 1, with parameters fx, fy, cx, cy.
    not_pinhole = sorted(name for name in intrinsics if models.get(camera_ids[name]) != 1)
    if not_pinhole:
        conn.close()
        raise RuntimeError(f"Database cameras are not PINHOLE: {not_pinhole}")
    rows = []
    seen = {}
    for name, (fx, fy, cx, cy) in intrinsics.items():
        camera_id = camera_ids[name]
        params = (float(fx), float(fy), float(cx), float(cy))
        previous = seen.setdefault(camera_id, params)
        if previous != params:
            conn.close()
            raise RuntimeError(f"Camera {camera_id} is shared by images with different intrinsics.")
        rows.append((struct.pack("<4d", *params), 1, camera_id))
    c.executemany(
        "UPDATE cameras SET params=?, prior_focal_length=? WHERE camera_id=?",
        rows,
    )
    conn.commit()
    conn.close()


def write_pose_priors(folder, positions):
    """Store camera-center priors. COLMAP treats them as soft constraints.

    ``positions`` maps an image name to an xyz camera center in world
    coordinates. CARTESIAN is coordinate system 1.
    """
    conn = sqlite3.connect(os.path.join(folder, "distorted", "database.db"))
    c = conn.cursor()
    c.execute("SELECT image_id, name FROM main.images")
    image_ids = {name: image_id for image_id, name in c.fetchall()}
    missing = sorted(set(positions) - set(image_ids))
    if missing:
        conn.close()
        raise RuntimeError(f"Pose prior images are missing from the database: {missing}")
    identity = struct.pack("<9d", 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    rows = [
        (
            image_ids[name],
            struct.pack("<3d", float(xyz), float(yz), float(zz)),
            1,
            identity,
        ) for name, (xyz, yz, zz) in positions.items()
    ]
    c.executemany(
        "INSERT INTO pose_priors(image_id, position, coordinate_system, position_covariance) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def pose_prior_mapper(folder, position_std, colmap_executable="colmap"):
    sparse_path = os.path.join(folder, "distorted", "sparse")
    os.makedirs(sparse_path, exist_ok=True)
    std = str(position_std)
    cmd = [
        colmap_executable, "pose_prior_mapper",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--image_path", os.path.join(folder, "input"),
        "--output_path", sparse_path,
        "--overwrite_priors_covariance", "1",
        "--prior_position_std_x", std,
        "--prior_position_std_y", std,
        "--prior_position_std_z", std,
        "--use_robust_loss_on_prior_position", "1",
        "--Mapper.ba_refine_focal_length", "0",
        "--Mapper.ba_refine_principal_point", "0",
        "--Mapper.ba_refine_extra_params", "0",
    ]
    return execute(cmd)


def mapper(folder, mapper_input_path=None, colmap_executable="colmap"):
    sparse_path = os.path.join(folder, "distorted", "sparse")
    os.makedirs(sparse_path, exist_ok=True)
    # A prior model is written directly into sparse/0. A from-scratch mapper
    # creates sparse/0 itself under the output directory.
    output_path = os.path.join(sparse_path, "0") if mapper_input_path else sparse_path
    os.makedirs(output_path, exist_ok=True)
    cmd = [
        colmap_executable, "mapper",
        "--database_path", os.path.join(folder, "distorted", "database.db"),
        "--image_path", os.path.join(folder, "input"),
        "--output_path", output_path,
        "--Mapper.ba_refine_focal_length", "0",
        "--Mapper.ba_refine_principal_point", "0",
        "--Mapper.ba_refine_extra_params", "0",
    ]
    if mapper_input_path:
        cmd += ["--input_path", mapper_input_path]
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


def model_writer_txt(folder, colmap_executable="colmap"):
    sparse_path = os.path.join(folder, "sparse")
    output_path = os.path.join(sparse_path, "0")
    os.makedirs(output_path, exist_ok=True)
    cmd = [
        colmap_executable, "model_converter",
        "--input_path", sparse_path,
        "--output_path", output_path,
        "--output_type=TXT",
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

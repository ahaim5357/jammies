"""A script containing the necessary methods for creating
and generating patches for a project.
"""

import os
from pathlib import PurePath
import shutil
from datetime import datetime
from project_patcher.singleton import METADATA_CODEC
from project_patcher.metadata.base import ProjectMetadata
from project_patcher.workspace.patcher import apply_patch, create_patch

_PATCH_EXTENSION: str = 'patch'
"""The extension of a patch file."""

# TODO: Expand to read files from GET request
# TODO: Expand to read metadata inside another json object
def read_metadata(path: str) -> ProjectMetadata:
    """TODO: Document"""

    with open(path, mode = 'r', encoding = 'UTF-8') as file:
        return METADATA_CODEC.decode(file.read())

def setup_clean(metadata: ProjectMetadata, clean_dir: str = 'clean',
        invalidate_cache: bool = False) -> bool:
    """TODO: Document"""

    # TODO: Move out and generalize
    clean_dir = os.path.join(os.curdir, clean_dir)

    # If the cache should be invalidated, delete the clean directory
    if invalidate_cache and os.path.exists(clean_dir) and os.path.isdir(clean_dir):
        shutil.rmtree(clean_dir)

    # If the cache exists, then skip generation
    ## Otherwise generate the metadata information
    return True if os.path.exists(clean_dir) and os.path.isdir(clean_dir) \
        else metadata.setup(clean_dir)

def apply_patches(working_dir: str = 'src', patch_dir: str = 'patches') -> bool:
    """TODO: Document"""

    # Assume both directories are present
    for subdir, _, files in os.walk(patch_dir):
        for file in files:
            patch_path: str = os.path.join(subdir, file)
            # Get the relative path of the file for the working directory
            rel_path: str = patch_path[(len(patch_dir) + 1):-(len(_PATCH_EXTENSION) + 1)]

            # Apply patch to working directory
            with open(patch_path, mode = 'r', encoding = 'UTF-8') as patch_file, \
                    open(os.path.join(working_dir, rel_path),
                        mode = 'r+', encoding = 'UTF-8') as work_file:
                work_patch: str = apply_patch(work_file.read(), patch_file.read())
                # Update work file with new information
                work_file.seek(0)
                work_file.write(work_patch)
                work_file.truncate()

    return True

def setup_working(clean_dir: str = 'clean', working_dir: str = 'src',
        patch_dir: str = 'patches', out_dir: str = 'out') -> bool:
    """TODO: Document"""

    # TODO: Move out and generalize
    clean_dir = os.path.join(os.curdir, clean_dir)
    working_dir = os.path.join(os.curdir, working_dir)
    patch_dir = os.path.join(os.curdir, patch_dir)
    out_dir = os.path.join(os.curdir, out_dir)

    # Remove existing working directory if exists
    if os.path.exists(working_dir) and os.path.isdir(working_dir):
        shutil.rmtree(working_dir)

    # Generate working directory (shouldn't exist)
    os.makedirs(working_dir)

    # Copy clean directory into working directory (clean directory must exist)
    shutil.copytree(clean_dir, working_dir, dirs_exist_ok = True)

    # If an output directory exists, copy into working directory
    if os.path.exists(out_dir) and os.path.isdir(out_dir):
        shutil.copytree(out_dir, working_dir, dirs_exist_ok = True)

    # If the patches directory exists, apply patches to working directory
    return apply_patches(working_dir, patch_dir) \
        if os.path.exists(patch_dir) and os.path.isdir(patch_dir) \
        else True

def output_working(clean_dir: str = 'clean', working_dir: str = 'src',
        patch_dir: str = 'patches', out_dir: str = 'out') -> bool:
    """TODO: Document"""

    # Current time
    time: str = str(datetime.now())

    # If patch directory and output exist, delete them
    if os.path.exists(out_dir) and os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    if os.path.exists(patch_dir) and os.path.isdir(patch_dir):
        shutil.rmtree(patch_dir)

    for subdir, _, files in os.walk(working_dir):
        for file in files:
            # Setup paths
            work_path: str = os.path.join(subdir, file)
            rel_path: str = work_path[(len(working_dir) + 1):]
            clean_path: str = os.path.join(clean_dir, rel_path)

            # If clean file exists, generate patch and write
            if os.path.exists(clean_path):
                with open(work_path, mode = 'r', encoding = 'UTF-8') as work_file, \
                        open(clean_path, mode = 'r', encoding = 'UTF-8') as clean_file:
                    # Generate patch file if not empty
                    if (patch_text := create_patch(clean_file.read(), work_file.read(),
                        filename = PurePath(rel_path).as_posix(),
                        time = time)):
                        patch_path: str = os.path.join(patch_dir,
                            os.extsep.join([rel_path, _PATCH_EXTENSION]))
                        # Create directory if necessary
                        os.makedirs(os.path.dirname(patch_path), exist_ok = True)
                        with open(patch_path, mode = 'w', encoding = 'UTF-8') as patch_file:
                            patch_file.write(patch_text)

            # Otherwise output files to directory
            else:
                out_path: str = os.path.join(out_dir, rel_path)
                # Create directory if necessary
                os.makedirs(os.path.dirname(out_path), exist_ok = True)
                shutil.copy(work_path, out_path)

    return True

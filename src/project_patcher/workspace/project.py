"""A script containing the necessary methods for creating
and generating patches for a project.
"""

import os
from pathlib import PurePath
import shutil
import json
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse
from requests import Response
from project_patcher.singleton import METADATA_CODEC, METADATA_BUILDER
from project_patcher.utils import download_file
from project_patcher.metadata.base import ProjectMetadata
from project_patcher.workspace.patcher import apply_patch, create_patch

_PROJECT_METADATA_NAME: str = 'project_metadata.json'
_PATCH_EXTENSION: str = 'patch'

"""The extension of a patch file."""

# TODO: Expand to read metadata inside another json object
def read_metadata(dirpath: str = os.curdir, import_loc: Optional[str] = None) -> ProjectMetadata:
    """Creates or reads project metadata for the current / to-be workspace.

    Parameters
    ----------
    dirpath : str (default '.')
        The directory of the (to-be) workspace.
    import_loc: str | None (default None)
        The location to read the project metadata from. Either a directory or a url.
    
    Returns
    -------
    project_patcher.metadata.base.ProjectMetadata
        The metadata for the current / to-be workspace.
    """

    # First check if an import is specified
    if import_loc is not None:
        # Check if import is a url
        if urlparse(import_loc).scheme in ('http', 'https'):
            json_bytes: bytes = None

            def get_metadata_str(response: Response) -> bool:
                """Reads the bytes of a response object into a higher scope variable.
                
                Parameters
                ----------
                response: response.Response
                    The response of the request.
                
                Returns
                -------
                bool
                    Whether the operation was successfully executed.
                """

                nonlocal json_bytes
                json_bytes = response.content
                return True

            # Download file
            if download_file(import_loc,
                lambda response, _: get_metadata_str(response),
                stream = False
            ):
                return write_metadata_to_file(dirpath,
                    METADATA_CODEC.decode(json.loads(json_bytes)))

        # Otherwise, assume import is a path and check if it exists
        elif os.path.exists(import_loc):
            return write_metadata_to_file(dirpath, read_metadata_from_file(import_loc))

    # If none, check if project metadata exists in directory
    if os.path.exists((path := os.sep.join([dirpath, _PROJECT_METADATA_NAME]))):
        return read_metadata_from_file(path)

    # Otherwise, open the builder
    return write_metadata_to_file(dirpath, METADATA_BUILDER())

def read_metadata_from_file(path: str) -> ProjectMetadata:
    """Reads a project metadata from a file location.

    Parameters
    ----------
    path : str
        The path to the project metadata JSON.

    Returns
    -------
    project_patcher.metadata.base.ProjectMetadata
        The metadata for the current / to-be workspace.
    """

    with open(path, mode = 'r', encoding = 'UTF-8') as file:
        return METADATA_CODEC.decode(json.load(file))

def write_metadata_to_file(dirpath: str, metadata: ProjectMetadata) -> ProjectMetadata:
    """Writes a project metadata, named `project_metadata.json`, to a file location.

    Parameters
    ----------
    dirpath : str
        The directory to write the project metadata to.
    metadata : project_patcher.metadata.base.ProjectMetadata
        The metadata for the current workspace.
    
    Returns
    -------
    metadata : project_patcher.metadata.base.ProjectMetadata
        The metadata for the current workspace.
    """

    with open(os.sep.join([dirpath, _PROJECT_METADATA_NAME]),
            mode = 'w', encoding = 'UTF-8') as file:
        json.dump(METADATA_CODEC.encode(metadata), file, indent = 4)

    return metadata

def setup_clean(metadata: ProjectMetadata, clean_dir: str = '_clean',
        invalidate_cache: bool = False) -> bool:
    """Generates a clean workspace from the project metadata.

    Parameters
    ----------
    metadata : project_patcher.metadata.base.ProjectMetadata
        The metadata for the current workspace.
    clean_dir : str (default '_clean')
        The directory to generate the clean workspace within.
    invalidate_cache : bool (default False)
        When `True`, removes any cached files for the clean workspace.
    
    Returns
    -------
    bool
        Whether the operation was successfully executed.
    """

    # If the cache should be invalidated, delete the clean directory
    if invalidate_cache and os.path.exists(clean_dir) and os.path.isdir(clean_dir):
        shutil.rmtree(clean_dir)

    # If the cache exists, then skip generation
    ## Otherwise generate the metadata information
    return True if os.path.exists(clean_dir) and os.path.isdir(clean_dir) \
        else metadata.setup(clean_dir)

def apply_patches(working_dir: str = '_src', patch_dir: str = '_patches') -> bool:
    """Applies patches to the working directory.

    Parameters
    ----------
    working_dir : str (default '_src')
        The directory containing the clean workspace to-be patched. 
    patch_dir : str (default '_patches')
        The directory containing the patches for the project files.
    
    Returns
    -------
    bool
        Whether the operation was successfully executed.
    """

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

def setup_working(clean_dir: str = '_clean', working_dir: str = '_src',
        patch_dir: str = '_patches', out_dir: str = '_out') -> bool:
    """Generates a working directory from the project metadata and any additional
    files and patches.

    Parameters
    ----------
    clean_dir : str (default '_clean')
        The directory containing the raw project files.
    working_dir : str (default '_src')
        The directory containing the clean workspace to-be patched. 
    patch_dir : str (default '_patches')
        The directory containing the patches for the project files.
    out_dir : str (default '_out')
        The directory containing additional files for the workspace.
    
    Returns
    -------
    bool
        Whether the operation was successfully executed.
    """

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

def generate_patch(path: str, work_path: str, clean_path: str,
        patch_dir: str = '_patches', time: str = str(datetime.now())) -> bool:
    """Generates a patch between two files if they are not equal.

    Parameters
    ----------
    path : str
        The relative path of the file.
    work_path : str
        The path of the file in the working directory.
    clean_path : str
        The path of the file in the clean directory.
    patch_dir : str (default '_patches')
        The directory containing the patches for the project files.
    time : str  (default `datetime.datetime.now`)
        The time the patch was generated.
    
    Returns
    -------
    bool
        Whether the operation was successfully executed.
    """

    # Assume patches directory exists

    with open(work_path, mode = 'r', encoding = 'UTF-8') as work_file, \
            open(clean_path, mode = 'r', encoding = 'UTF-8') as clean_file:
        # Generate patch file if not empty
        if (patch_text := create_patch(clean_file.read(), work_file.read(),
                filename = PurePath(path).as_posix(),
                time = time)):
            patch_path: str = os.path.join(patch_dir,
                os.extsep.join([path, _PATCH_EXTENSION]))
            # Create directory if necessary
            os.makedirs(os.path.dirname(patch_path), exist_ok = True)
            with open(patch_path, mode = 'w', encoding = 'UTF-8') as patch_file:
                patch_file.write(patch_text)

    return True

def output_file(path: str, work_path: str, out_dir: str = '_out') -> bool:
    """Copies an additional file for the workspace to the output directory.
    
    Parameters
    ----------
    path : str
        The relative path of the file.
    work_path : str
        The path of the file in the working directory.
    out_dir : str (default '_out')
        The directory containing additional files for the workspace.

    Returns
    -------
    bool
        Whether the operation was successfully executed.
    """

    # Assume output directory exists

    out_path: str = os.path.join(out_dir, path)
    # Create directory if necessary
    os.makedirs(os.path.dirname(out_path), exist_ok = True)
    shutil.copy(work_path, out_path)

    return True

def output_working(clean_dir: str = '_clean', working_dir: str = '_src',
        patch_dir: str = '_patches', out_dir: str = '_out') -> bool:
    """Generates the patches and copies any additional files for construction.
    
    Parameters
    ----------
    clean_dir : str (default '_clean')
        The directory containing the raw project files.
    working_dir : str (default '_src')
        The directory containing the clean workspace to-be patched. 
    patch_dir : str (default '_patches')
        The directory containing the patches for the project files.
    out_dir : str (default '_out')
        The directory containing additional files for the workspace.

    Returns
    -------
    bool
        Whether the operation was successfully executed.
    """

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
                generate_patch(rel_path, work_path, clean_path, patch_dir = patch_dir, time = time)

            # Otherwise output files to directory
            else:
                output_file(rel_path, work_path, out_dir = out_dir)

    return True

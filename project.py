import os
import shutil
import pathlib
from patcher import make_patch, apply_patch

CLEAN_DIR: str = os.path.join(os.curdir, 'clean')
WORKING_DIR: str = os.path.join(os.curdir, 'src')
OUTPUT_DIR: str = os.path.join(os.curdir, 'out')
PATCH_DIR = os.path.join(os.curdir, 'patches')
PATCH_EXTENSION = '.patch'

# TODO: Make this smarter to not copy unnecessary files
def create_working_dir() -> None:
    # Create working directory if not present
    os.makedirs(WORKING_DIR, exist_ok = True)

    # Copy clean directory into working directory
    shutil.copytree(CLEAN_DIR, WORKING_DIR, dirs_exist_ok = True)

    # Copy output directory into working directory
    shutil.copytree(OUTPUT_DIR, WORKING_DIR, dirs_exist_ok = True)

    # Apply patches to working directory
    for subdir, _, files in os.walk(PATCH_DIR):
        for file in files:
            patch_path: str = os.path.join(subdir, file)
            rel_path: str = patch_path[(len(PATCH_DIR) + 1):-(len(PATCH_EXTENSION))]
            
            with open(patch_path, 'r') as patch_file, open(os.path.join(WORKING_DIR, rel_path), 'r+') as work_file:
                work_patch: str = apply_patch(work_file.read(), patch_file.read())
                work_file.seek(0)
                work_file.write(work_patch)
                work_file.truncate()

# TODO: Make this smarter for git and other things when files shouldn't be outputted
def gen_patches():
    # Generate patch directory if not present
    os.makedirs(PATCH_DIR, exist_ok = True)

    for subdir, _, files in os.walk(WORKING_DIR):
        for file in files:
            work_path: str = os.path.join(subdir, file)
            rel_path: str = work_path[(len(WORKING_DIR) + 1):]
            clean_path: str = os.path.join(CLEAN_DIR, rel_path)

            # Check if clean file exists
            if os.path.exists(clean_path):
                with open(work_path, 'r') as work_file, open(clean_path, 'r') as clean_file:
                    # Generated diff and patch file if necessary
                    patch_text: str = make_patch(clean_file.read(), work_file.read(), filename = pathlib.PurePath(rel_path).as_posix())
                    if patch_text:
                        # Make directories if not exists
                        patch_path: str = os.path.join(PATCH_DIR, f'{rel_path}.patch')
                        os.makedirs(os.path.dirname(patch_path), exist_ok = True)

                        with open(patch_path, 'w') as patch_file:
                            patch_file.write(patch_text)
            else:
                # Make output directories if not present
                out_path: str = os.path.join(OUTPUT_DIR, rel_path)
                os.makedirs(os.path.dirname(out_path), exist_ok = True)

                shutil.copy(work_path, out_path)

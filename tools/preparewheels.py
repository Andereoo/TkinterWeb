"""
Wheel and sdist generator for TkinterWeb

Copyright (c) 2025 Andereoo
"""

import os, shutil, sys
import subprocess

PYTHON_CMD = "python3"

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DIST_ROOT_PATH = os.path.join(ROOT_PATH, "dist")
BUILD_ROOT_PATH = os.path.join(ROOT_PATH, "build")
EGG_ROOT_PATH = os.path.join(ROOT_PATH, "tkinterweb.egg-info")
TKINTERWEB_ROOT_PATH = os.path.join(ROOT_PATH, "tkinterweb")

existing_folders = []
if os.path.exists(DIST_ROOT_PATH):
    existing_folders.append(DIST_ROOT_PATH)
if os.path.exists(BUILD_ROOT_PATH):
    existing_folders.append(BUILD_ROOT_PATH)
if os.path.exists(EGG_ROOT_PATH):
    existing_folders.append(EGG_ROOT_PATH)

if existing_folders:
    should_continue = input("The following directories already exist:\n    {} \nRemove and continue (Y/N)? ".format("\n    ".join(existing_folders)))
    if should_continue.upper() == "Y":
        print()
        for path in existing_folders:
            print(f"Removing {path}")
            shutil.rmtree(path)
    else:
        print("Cancelling")
        #exit()

print()

def run_shell(*args, cwd=ROOT_PATH, is_wheel=False):
    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode('utf-8')
    if is_wheel and "Successful" in out:
        print("success!\n")
    else:
        print(f"\n{out}")
    if err:
        err = err.decode('utf-8').replace("\n\n", "\n") # For some reason some errors have tons of blank space
        print(f"Error: {err}", file=sys.stderr)

print(f"Creating wheel and sdist for {TKINTERWEB_ROOT_PATH}...", end="")
run_shell(PYTHON_CMD, "-m", "build", "--no-isolation", is_wheel=True)
        
# Upload to pip
should_continue = input("Upload to pip (Y/N)?")
if should_continue.upper() == "Y":
    run_shell("twine", "upload", "dist/*", "-u", "__token__")

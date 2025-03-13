"""
A wheel and sdist generator for TkinterWeb

This script will generate a universal wheel, a universal sdist, and platform-specific wheels for TkinterWeb
It's a pretty messy solution but makes it possible to only bundle only the tkhtml binary needed in each platform-specific wheel
This avoids the need to have a seperate copy of the repository for each platform

Copyright (c) 2025 Andereoo
"""

import os, shutil, sys
import subprocess
import re

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
WHEELS_ROOT_PATH = os.path.join(ROOT_PATH, "wheels")
DIST_ROOT_PATH = os.path.join(ROOT_PATH, "dist")
BUILD_ROOT_PATH = os.path.join(ROOT_PATH, "build")
EGG_ROOT_PATH = os.path.join(ROOT_PATH, "tkinterweb.egg-info")
TKINTERWEB_ROOT_PATH = os.path.join(ROOT_PATH, "tkinterweb")
TKINTERWEB_NEW_ROOT_PATH = os.path.join(WHEELS_ROOT_PATH, "tkinterweb_")
TKHTML_ROOT_PATH = os.path.join(TKINTERWEB_ROOT_PATH, "tkhtml")
README_PATH = os.path.join(ROOT_PATH, "README.md")
LICENCE_PATH = os.path.join(ROOT_PATH, "LICENSE.md")
SETUP_PATH = os.path.join(ROOT_PATH, "setup.py")
MANIFEST_PATH = os.path.join(ROOT_PATH, "MANIFEST.in")
TKHTML_SUBFOLDER_NAME = "binaries"

manifest_in_contents = "recursive-include tkinterweb/tkhtml *"
setup_py_contents_generic = """import pathlib, platform
from setuptools import setup, find_namespace_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
{}

extras = dict()
extras["javascript"] = ["pythonmonkey"]
if platform.system() == "Linux":
    extras["svg"] = ["pygobject", "pycairo"]
else:
    extras["svg"] = ["cairosvg"]
extras["full"] = extras["javascript"] + extras["svg"]

setup(
    name="tkinterweb",
    version="4.1.0",
    description="HTML/CSS viewer for Tkinter",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Andereoo/TkinterWeb",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: Freeware",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
      ],
    keywords="tkinter, Tkinter, tkhtml, Tkhtml, Tk, HTML, CSS, webbrowser",
    packages=find_namespace_packages(include=["tkinterweb", "tkinterweb.*"]),
    include_package_data=True,
    install_requires=["pillow"],
    extras_require = extras,
{}
)
print("The API changed in version 4. See https://github.com/Andereoo/TkinterWeb for details.")
"""
setup_py_contents = setup_py_contents_generic.format("""
def get_platname():
    return "{}"                                                      
""", """
    options={{
        "bdist_wheel": {{
            "plat_name": get_platname(),
        }},
    }}, 
""")

existing_folders = []
if os.path.exists(WHEELS_ROOT_PATH):
    existing_folders.append(WHEELS_ROOT_PATH)
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

### Create a wheel for each supported platform
tkhtml_folders = {}
for f in os.scandir(TKHTML_ROOT_PATH):
    if f.is_dir():
        tkhtml_folders[f.name] = f.path


def run_shell(*args, cwd=ROOT_PATH, is_wheel=False):
    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode('ascii')
    if is_wheel and "Successful" in out:
        print("success!\n")
    else:
        print(f"\n{out}")
    if err:
        err = err.decode('ascii').replace("\n\n", "\n") # For some reason some errors have tons of blank space
        print(f"Error: {err}", file=sys.stderr)


def copyfolder(src, dst, keep, ignore):
    os.mkdir(dst)
    for path, directories, files in os.walk(src):
        if os.path.basename(path) in ignore:
            continue

        for directory in directories:
            if directory not in ignore:
                directory_src_path = os.path.join(path, directory)
                if directory == keep:
                    directory = TKHTML_SUBFOLDER_NAME
                directory_dst_path = os.path.join(path.replace(src, dst), directory)
                os.mkdir(directory_dst_path)
                #copyfolder(directory_src_path, directory_dst_path, keep, ignore)
        for file in files:
            new_folder = path.replace(src, dst)
            if os.path.basename(new_folder) == keep:
                new_folder = os.path.join(os.path.dirname(new_folder), TKHTML_SUBFOLDER_NAME)
            if file == "utilities.py":
                with open(os.path.join(path, file), "r") as handle:
                    content = handle.read()
                    content = re.sub(r"# Universal sdist((.|\n)*?)# Platform-specific wheel", "# Platform-specific wheel", content, re.MULTILINE) # Remove code for universal sdist
                    # re.sub(r"# Platform-specific wheel((.|\n)*?)\n\n", "", s, re.MULTILINE) # Remove code for platform-specific wheels
                with open(os.path.join(new_folder, file), "w+") as handle:
                    handle.write(content)
            else:
                shutil.copy2(os.path.join(path, file), new_folder)

print(f"Using source directory {TKINTERWEB_ROOT_PATH}")
print("Found {} supported platforms: {}\n".format(len(tkhtml_folders), ", ".join(tkhtml_folders)))

wheel_folders_to_copy = []
os.mkdir(WHEELS_ROOT_PATH)
for folder in tkhtml_folders:
    folders = list(tkhtml_folders.keys())
    folders.remove(folder)
    folder_path = TKINTERWEB_NEW_ROOT_PATH + folder
    os.mkdir(folder_path)

    print(f"Generating {folder_path}")        
    copyfolder(TKINTERWEB_ROOT_PATH, os.path.join(folder_path, os.path.basename(TKINTERWEB_ROOT_PATH)), folder, folders)
    
    setup_path = os.path.join(folder_path, "setup.py")
    with open(setup_path, "w+") as handle:
        handle.write(setup_py_contents.format(folder))

    shutil.copy2(README_PATH, folder_path)
    shutil.copy2(LICENCE_PATH, folder_path)
    shutil.copy2(MANIFEST_PATH, folder_path)
    
    print(f"Creating wheel for {folder}...", end="")
    run_shell("python3", "-m", "build", "--no-isolation", "--wheel", cwd=folder_path, is_wheel=True)    
    wheel_folders_to_copy.append(os.path.join(folder_path, "dist"))
    
# Check if setup.py exises
if os.path.exists(SETUP_PATH) :
    should_continue = input("The generic setup.py file already exists. Update and continue (Y/N)? ")
    if should_continue.upper() == "Y":
        print()
        os.remove(SETUP_PATH)
    else:
        print("Cancelling")
        exit()

with open(SETUP_PATH, "w+") as handle:
    handle.write(setup_py_contents_generic.format("", ""))

print(f"Creating wheel and sdist for {TKINTERWEB_ROOT_PATH}...", end="")
run_shell("python3", "-m", "build", "--no-isolation", is_wheel=True)

# Copy all wheels to the main dist folder
print(f"Copying wheels to {DIST_ROOT_PATH}\n")
for folder in wheel_folders_to_copy:
    for wheel in os.listdir(folder):
        shutil.copy2(os.path.join(folder, wheel), os.path.join(DIST_ROOT_PATH, wheel))

        
# Upload to pip
#should_continue = input("Upload to pip (Y/N)?")
#if should_continue.upper() == "Y":
#    run_shell("twine", "upload", "dist/*", "-u", "__token__")
#twine upload dist/* -u __token__

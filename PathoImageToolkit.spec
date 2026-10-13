# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import (
    collect_all,
    collect_dynamic_libs,
    collect_submodules,
    collect_data_files,
    copy_metadata,
)

block_cipher = None

# ============================================================
# Paths
# ============================================================

project_root = os.path.abspath(".")
openslide_path = os.path.join(project_root, "openslide_bin")
assets_path = os.path.join(project_root, "assets")
icon_path = os.path.join(assets_path, "icon", "pathoimage.ico")

# ============================================================
# Collect compiled / package dependencies
# ============================================================

imagecodecs_datas, imagecodecs_binaries, imagecodecs_hiddenimports = collect_all("imagecodecs")
numcodecs_datas, numcodecs_binaries, numcodecs_hiddenimports = collect_all("numcodecs")
zarr_datas, zarr_binaries, zarr_hiddenimports = collect_all("zarr")

# Olympus/Evident VSI support. BFIO uses dynamic imports, JPype, scyjava/jgo,
# cjdk and a compiled bfiocpp extension, so collect them explicitly.
vsi_packages = (
    "bfio",
    "bfiocpp",
    "ome_types",
    # ome-types 0.6.x ships additional top-level packages that are imported
    # dynamically through xsdata hooks. They are siblings of ome_types, so
    # collecting ome_types alone does not make PyInstaller include them.
    "xsdata_pydantic_basemodel",
    "xsdata",
    "pydantic",
    "pydantic_core",
    "pydantic_extra_types",
    "scyjava",
    "jpype",
    "jgo",
    "cjdk",
)
vsi_datas = []
vsi_binaries = []
vsi_hiddenimports = []
for package_name in vsi_packages:
    _datas, _binaries, _hidden = collect_all(package_name)
    vsi_datas += _datas
    vsi_binaries += _binaries
    vsi_hiddenimports += _hidden

# PyInstaller does not include distribution metadata merely because a package is
# collected. scyjava/jgo/cjdk and parts of the BFIO stack may query installed
# distributions at runtime, so preserve the metadata explicitly. Recursive BFIO
# metadata also covers its declared dependencies.
vsi_metadata = []
for distribution_name in (
    "bfio", "scyjava", "jgo", "cjdk", "JPype1", "ome-types", "bfiocpp",
    "xsdata", "pydantic", "pydantic-extra-types"
):
    try:
        vsi_metadata += copy_metadata(distribution_name, recursive=(distribution_name == "bfio"))
    except Exception:
        # Some platform-specific wheels/distribution names may not exist during a
        # build. The explicit package collection above remains the primary path.
        pass

# Leica LIF support.
# readlif is imported lazily in the app, so PyInstaller may not detect it
# unless it is explicitly collected here.
readlif_hiddenimports = collect_submodules("readlif")
bs4_hiddenimports = collect_submodules("bs4")
soupsieve_hiddenimports = collect_submodules("soupsieve")

readlif_datas = collect_data_files("readlif")
bs4_datas = collect_data_files("bs4")
soupsieve_datas = collect_data_files("soupsieve")

# OpenSlide dynamic libraries if available as package binaries.
openslide_binaries = collect_dynamic_libs("openslide")

# ============================================================
# Data files
# ============================================================

datas = []

if os.path.isdir(openslide_path):
    datas.append((openslide_path, "openslide_bin"))

if os.path.isdir(assets_path):
    datas.append((assets_path, "assets"))

datas += imagecodecs_datas
datas += numcodecs_datas
datas += zarr_datas
datas += vsi_datas
datas += vsi_metadata
datas += readlif_datas
datas += bs4_datas
datas += soupsieve_datas

# ============================================================
# Binaries
# ============================================================

binaries = []
binaries += imagecodecs_binaries
binaries += numcodecs_binaries
binaries += zarr_binaries
binaries += vsi_binaries
binaries += openslide_binaries

# ============================================================
# Hidden imports
# ============================================================

hiddenimports = [
    "numpy",
    "PIL",
    "PIL.Image",
    "tifffile",
    "zarr",
    "numcodecs",
    "imagecodecs",
    "openslide",

    # Olympus / Evident VSI support
    "bfio",
    "bfiocpp",
    "ome_types",
    "xsdata_pydantic_basemodel",
    "xsdata_pydantic_basemodel.hooks",
    "xsdata",
    "pydantic",
    "pydantic_core",
    "pydantic_extra_types",
    "scyjava",
    "jpype",
    "jgo",
    "cjdk",

    # Leica LIF support
    "readlif",
    "readlif.reader",
    "bs4",
    "bs4.builder",
    "bs4.builder._htmlparser",
    "soupsieve",

    # Extra safety for imagecodecs compiled modules
    "imagecodecs._shared",
    "imagecodecs._imcd",
    "imagecodecs._aec",
    "imagecodecs._bitshuffle",
    "imagecodecs._brotli",
    "imagecodecs._deflate",
    "imagecodecs._jpeg2k",
    "imagecodecs._jpeg8",
    "imagecodecs._jpegsof3",
    "imagecodecs._lz4",
    "imagecodecs._lzf",
    "imagecodecs._lzma",
    "imagecodecs._png",
    "imagecodecs._tiff",
    "imagecodecs._webp",
    "imagecodecs._zlib",
    "imagecodecs._zopfli",
    "imagecodecs._zstd",
]

hiddenimports += imagecodecs_hiddenimports
hiddenimports += numcodecs_hiddenimports
hiddenimports += zarr_hiddenimports
hiddenimports += vsi_hiddenimports
hiddenimports += readlif_hiddenimports
hiddenimports += bs4_hiddenimports
hiddenimports += soupsieve_hiddenimports

# Remove duplicates while preserving order
hiddenimports = list(dict.fromkeys(hiddenimports))

# ============================================================
# Analysis
# ============================================================

a = Analysis(
    ["src/pathoimage_toolkit/app.py"],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ============================================================
# Single-file executable
# ============================================================

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PathoImageToolkit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icon_path if os.path.exists(icon_path) else None,
)

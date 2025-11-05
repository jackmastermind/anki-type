#!/usr/bin/env python3
"""
Build script for creating .ankiaddon package.

This script:
1. Cleans __pycache__ directories
2. Creates a .ankiaddon zip file with proper structure
3. Names the file based on version in manifest.json
"""

import json
import os
import shutil
import zipfile
from pathlib import Path

# Files to include in the add-on package
INCLUDE_FILES = [
    "__init__.py",
    "manifest.json",
    "README.md",
    "LICENSE",
]


def clean_pycache(root_dir: Path) -> None:
    """Remove all __pycache__ directories."""
    print("Cleaning __pycache__ directories...")
    for pycache_dir in root_dir.rglob("__pycache__"):
        print(f"  Removing {pycache_dir}")
        shutil.rmtree(pycache_dir)


def get_version(manifest_path: Path) -> str:
    """Extract version from manifest.json."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest.get("version", "unknown")


def create_ankiaddon(root_dir: Path, output_dir: Path, version: str) -> Path:
    """
    Create .ankiaddon file.

    Important: The zip should NOT include the top-level folder.
    Files should be at the root of the zip.
    """
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"anki-type-{version}.ankiaddon"

    print(f"\nCreating {output_file.name}...")

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_name in INCLUDE_FILES:
            file_path = root_dir / file_name
            if file_path.exists():
                # Add file at root of zip (no parent folder)
                print(f"  Adding {file_name}")
                zf.write(file_path, file_name)
            else:
                print(f"  Warning: {file_name} not found, skipping")

    return output_file


def main():
    """Main build process."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent

    print(f"Building add-on from: {script_dir}\n")

    # Clean __pycache__
    clean_pycache(script_dir)

    # Get version from manifest
    manifest_path = script_dir / "manifest.json"
    version = get_version(manifest_path)
    print(f"Version: {version}\n")

    # Create output directory
    output_dir = script_dir / "dist"

    # Create .ankiaddon file
    output_file = create_ankiaddon(script_dir, output_dir, version)

    # Get file size
    size_bytes = output_file.stat().st_size
    size_kb = size_bytes / 1024

    print(f"\n✓ Build complete!")
    print(f"  Output: {output_file}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"\nYou can now upload {output_file.name} to AnkiWeb at:")
    print("  https://ankiweb.net/shared/addons/")


if __name__ == "__main__":
    main()

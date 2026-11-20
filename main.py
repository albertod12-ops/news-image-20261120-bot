#!/usr/bin/env python3
"""Copy the finished 20 November 2026 front page to the grader's output dir.

The repository holds the finished picture as entry.png (1024x1024, under
1 MiB). This entrypoint does one thing: copy that file to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), byte for byte, with no
network access and no randomness.

A missing source, an empty source, a source that is not a PNG file, or a
copy that does not match the source byte for byte is a loud failure
(exit 1), never a partial entry.

Run it locally the same way the grader does, with an output directory
of your own:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

# v1 entry (2026-11-20): thirteen flat-vector pictures, the day's front 13.
import hashlib
import os
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run():
    if not SOURCE.is_file():
        print(f"missing source: {SOURCE}", file=sys.stderr)
        return 1
    if SOURCE.stat().st_size == 0:
        print(f"empty source: {SOURCE}", file=sys.stderr)
        return 1
    with open(SOURCE, "rb") as handle:
        if handle.read(8) != PNG_MAGIC:
            print(f"source is not a PNG file: {SOURCE}", file=sys.stderr)
            return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    if file_sha256(SOURCE) != file_sha256(target):
        print("copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

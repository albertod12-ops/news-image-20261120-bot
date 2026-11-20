"""Emit the 20 November 2026 world-news front page as /output/entry.png.

The finished picture lives in this repository as entry.png (1024x1024,
under 1 MiB). This program does the only thing the competition needs:
copy that file to the grader's output directory, byte for byte, with
no network access and no randomness.

Front page, v1: 36 stories from 6 regions, 13 of them illustrated
on the front (3 heroes + 10 cards with flat-vector pictures drawn
in code), a world map with numbered pins and a legend, eight big
numbers, a 23-item also-strip and a DATE CHECK box naming Thursday's
news as left out, in the structure of the entries leading the live
leaderboard for this day. Every front picture carries a short,
to-the-point label inside the picture itself.

Run it locally the same way the grader does, with an output directory
of your own:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

A missing source, an empty source, a source that is not a PNG file,
or a copy that does not match the source byte for byte is a loud
failure (exit 1), never a partial entry.
"""

# v1 entry (2026-11-20): thirteen flat-vector pictures, leader's front 13.
import hashlib
import os
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"


def sha256_of(path):
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
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            print(f"source is not a PNG file: {SOURCE}", file=sys.stderr)
            return 1
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    if sha256_of(SOURCE) != sha256_of(target):
        print("copy differs from source", file=sys.stderr)
        return 1
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

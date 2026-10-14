#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate original geometric PNG/JPEG fixtures for illustration rendering."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

SIZE = 192
ROOT = Path(__file__).resolve().parent
FIXTURES = [
    ("I23-01", "transparent-shapes.png", "透明背景・モノクロ図形"),
    ("I23-02", "white-shapes.png", "白背景・モノクロPNG"),
    ("I23-03", "white-shapes.jpg", "白背景・モノクロJPEG"),
    ("I23-04", "color-shapes.png", "白背景・カラーPNG"),
    ("I23-05", "color-shapes.jpg", "白背景・カラーJPEG"),
    ("I23-06", "offwhite-shapes.png", "灰色背景・モノクロPNG"),
    ("I23-07", "dense-white-20.png", "墨が多い・白地約20％"),
    ("I23-08", "dense-white-5.png", "墨が多い・白地約5％"),
    ("I23-09", "sparse-ink-0_3.png", "墨が少ない・墨約0.3％"),
    ("I23-10", "sparse-ink-1.png", "墨が増えた・墨約1％"),
    ("I23-11", "blank-white.png", "白一色"),
]


def canvas(background):
    return bytearray(background * (SIZE * SIZE))


def rectangle(data, left, top, right, bottom, color):
    # 終端を含めず、面積比を再現できる整数座標で描くルン。
    for y in range(top, bottom):
        for x in range(left, right):
            offset = (y * SIZE + x) * 4
            data[offset:offset + 4] = bytes(color)


def outline(data, left, top, right, bottom, color, thickness=4):
    rectangle(data, left, top, right, top + thickness, color)
    rectangle(data, left, bottom - thickness, right, bottom, color)
    rectangle(data, left, top, left + thickness, bottom, color)
    rectangle(data, right - thickness, top, right, bottom, color)


def triangle(data, color):
    # 右三角形を走査線で描き、外部素材やフォントを使わないルン。
    for y in range(58, 119):
        right = 110 + (y - 58) * 66 // 60
        rectangle(data, 110, y, right + 1, y + 1, color)


def shapes(background, colored=False):
    data = canvas(background)
    black = (0, 0, 0, 255)
    rectangle(data, 18, 26, 174, 30, black)
    outline(data, 18, 56, 80, 118, black)
    triangle(data, (30, 90, 210, 255) if colored else (96, 96, 96, 255))
    rectangle(data, 20, 142, 64, 174, (210, 45, 40, 255) if colored else (0, 0, 0, 255))
    outline(data, 94, 136, 156, 174, (30, 145, 65, 255) if colored else (128, 128, 128, 255))
    return data


def png_bytes(data):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
    # RGBAのPNGにし、透明背景と不透明背景を同じ図形で比較するルン。
    rows = b"".join(b"\x00" + data[y * SIZE * 4:(y + 1) * SIZE * 4] for y in range(SIZE))
    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def generate(output):
    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick (magick) is required only when regenerating the JPEG fixtures")
    output.mkdir(parents=True, exist_ok=True)
    images = {
        "transparent-shapes.png": shapes((0, 0, 0, 0)),
        "white-shapes.png": shapes((255, 255, 255, 255)),
        "color-shapes.png": shapes((255, 255, 255, 255), colored=True),
        "offwhite-shapes.png": shapes((230, 230, 230, 255)),
        "blank-white.png": canvas((255, 255, 255, 255)),
    }
    for name, side in [("dense-white-20.png", 86), ("dense-white-5.png", 44)]:
        data = canvas((0, 0, 0, 255))
        start = (SIZE - side) // 2
        rectangle(data, start, start, start + side, start + side, (255, 255, 255, 255))
        images[name] = data
    for name, width, height in [("sparse-ink-0_3.png", 54, 2), ("sparse-ink-1.png", 100, 4)]:
        data = canvas((255, 255, 255, 255))
        left, top = (SIZE - width) // 2, (SIZE - height) // 2
        rectangle(data, left, top, left + width, top + height, (0, 0, 0, 255))
        images[name] = data
    for name, data in images.items():
        (output / name).write_bytes(png_bytes(data))
    for stem in ("white-shapes", "color-shapes"):
        subprocess.run([
            magick, str(output / f"{stem}.png"), "-background", "white", "-alpha", "remove",
            "-strip", "-sampling-factor", "4:4:4", "-quality", "92", str(output / f"{stem}.jpg")
        ], check=True)
    print(f"Generated {len(FIXTURES)} image fixtures in {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "EPUB/images")
    args = parser.parse_args()
    generate(args.output)


if __name__ == "__main__":
    main()

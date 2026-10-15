#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the embedded font fixture with HarfBuzz hb-subset."""
import argparse
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = "769b5269f0f9bc6534b352c0e6bd856a566e03ff788f107191c2d835863570b2"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Pinned ShipporiMincho-Regular.ttf")
    args = parser.parse_args()
    if hashlib.sha256(args.source.read_bytes()).hexdigest() != SOURCE_SHA256:
        parser.error("Source font SHA-256 does not match the documented version")
    output = ROOT / "EPUB/fonts/ShipporiMincho-Regular-test-subset.ttf"
    output.parent.mkdir(parents=True, exist_ok=True)
    # 文字だけを絞り、縦組み用の字形・組版機能と著作権情報は残すルン。
    subprocess.run([
        "hb-subset", str(args.source), f"--text-file={ROOT / 'font_probe.txt'}",
        "--layout-features=*", "--name-IDs=*", "--name-languages=*",
        f"--output-file={output}",
    ], check=True)
    print(f"Generated {output.name}: {output.stat().st_size} bytes")
    print(f"SHA-256: {hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()

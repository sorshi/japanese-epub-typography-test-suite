#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build a deterministic EPUB 3 archive from source files."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
PROJECT_NAME = "japanese-epub-typography-test-suite"
MIMETYPE = ROOT / "mimetype"
CONTAINER = ROOT / "META-INF" / "container.xml"
PACKAGE = ROOT / "EPUB" / "package.opf"
NS = {
    "h": "http://www.w3.org/1999/xhtml",
    "opf": "http://www.idpf.org/2007/opf",
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
}
ARCHIVE_DATE = (2026, 10, 14, 22, 32, 43)


def local_target(source: Path, href: str) -> tuple[Path, str]:
    # ローカル参照はソース内に解決し、誤ったリンクを配布前に検出するルン。
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or parts.query:
        raise ValueError(f"Expected a local reference in {source.name}: {href}")
    target = (source.parent / unquote(parts.path)).resolve() if parts.path else source.resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
        raise ValueError(f"Missing or out-of-tree reference in {source.name}: {href}")
    return target, unquote(parts.fragment)


def check_sources() -> list[Path]:
    if MIMETYPE.read_bytes() != b"application/epub+zip":
        raise ValueError("mimetype must contain exactly application/epub+zip")
    for path in (CONTAINER, PACKAGE):
        if not path.is_file():
            raise FileNotFoundError(path)
    resources = sorted(
        (p for name in ("META-INF", "EPUB") for p in (ROOT / name).rglob("*") if p.is_file() and p.name != ".DS_Store"),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    documents = {}
    identifiers = {}
    for path in resources:
        if path.suffix in (".xml", ".opf", ".xhtml", ".ncx", ".svg"):
            document = ElementTree.parse(path)
            documents[path.resolve()] = document
            ids = [element.attrib["id"] for element in document.iter() if "id" in element.attrib]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Duplicate IDs: {path.name}")
            identifiers[path.resolve()] = set(ids)
    container = documents[CONTAINER.resolve()]
    rootfile = container.find("container:rootfiles/container:rootfile", NS)
    if rootfile is None or rootfile.get("full-path") != "EPUB/package.opf":
        raise ValueError("container.xml must reference EPUB/package.opf")
    package = documents[PACKAGE.resolve()]
    manifest = {}
    nav_paths = []
    for item in package.findall("opf:manifest/opf:item", NS):
        target, fragment = local_target(PACKAGE, item.attrib["href"])
        if fragment:
            raise ValueError("Manifest references cannot have fragments")
        manifest[item.attrib["id"]] = target
        if "nav" in item.get("properties", "").split():
            nav_paths.append(target)
    expected = {p.resolve() for p in resources if p.is_relative_to(ROOT / "EPUB") and p != PACKAGE}
    if set(manifest.values()) != expected or len(manifest) != len(expected):
        raise ValueError("Manifest must list each EPUB resource exactly once")
    if len(nav_paths) != 1:
        raise ValueError("Exactly one navigation document is required")
    spine = []
    for item in package.findall("opf:spine/opf:itemref", NS):
        target = manifest.get(item.attrib["idref"])
        if target is None or target.suffix != ".xhtml":
            raise ValueError(f"Invalid spine reference: {item.attrib['idref']}")
        spine.append(target)
    chapters = sorted((ROOT / "EPUB").glob("chapter*.xhtml"))
    reading_order = [ROOT / "EPUB/cover.xhtml", *chapters, ROOT / "EPUB/colophon.xhtml"]
    if spine != [p.resolve() for p in reading_order]:
        raise ValueError("Spine must contain cover, all chapters in order, and colophon")
    nav = documents[nav_paths[0]]
    toc = nav.find(".//h:nav[@id='toc']", NS)
    if toc is None:
        raise ValueError("Missing table of contents")
    toc_paths = [local_target(nav_paths[0], a.attrib["href"])[0] for a in toc.findall(".//h:a", NS)]
    if toc_paths != spine:
        raise ValueError("Table of contents must match spine order")
    colophon = documents[(ROOT / "EPUB/colophon.xhtml").resolve()]
    license_section = colophon.find(".//h:section[@id='mit-license']", NS)
    license_text = ROOT / "LICENSE"
    if license_section is None or " ".join(license_section.itertext()).split() != license_text.read_text(encoding="utf-8").split():
        raise ValueError("Colophon must contain the complete LICENSE text")
    covers = package.findall("opf:manifest/opf:item[@properties='cover-image']", NS)
    if len(covers) != 1 or covers[0].get("href") != "cover.png":
        raise ValueError("Exactly one cover.png cover-image is required")
    for path, document in documents.items():
        for element in document.iter():
            for attribute in ("href", "src"):
                href = element.get(attribute)
                if href is None:
                    continue
                if urlsplit(href).scheme in ("https", "http") and element.tag == f"{{{NS['h']}}}a":
                    continue
                target, fragment = local_target(path, href)
                if fragment and fragment not in identifiers.get(target, set()):
                    raise ValueError(f"Missing fragment in {path.name}: {href}")
    chapter = (ROOT / "EPUB" / "chapter22.xhtml").read_text(encoding="utf-8")
    for pair in ("〳〵", "〴〵"):
        if pair not in chapter:
            raise ValueError(f"Missing contiguous character test: {pair}")
    unicode_doc = documents[(ROOT / "EPUB" / "chapter33.xhtml").resolve()]
    unicode_sample = unicode_doc.find(".//h:p[@id='unicode-copy']", NS)
    if unicode_sample is None or unicode_sample.text != "が／か\u3099／ｶﾞ／葛\U000E0100／𠮷":
        raise ValueError("Unicode test sequences were changed or normalized")
    # CSSのimport先と埋め込みフォントも、配布前に参照切れを検出するルン。
    for path in resources:
        if path.suffix == ".css":
            css = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
            references = re.findall(r'url\(\s*[\"\']?([^\"\'\s)]+)', css)
            references += re.findall(r'@import\s+[\"\']([^\"\']+)', css)
            for href in references:
                target, _ = local_target(path, href)
                if target not in manifest.values():
                    raise ValueError(f"CSS reference is not in the manifest: {href}")
    font_license = documents[(ROOT / "EPUB/colophon.xhtml").resolve()]
    paragraphs = font_license.findall(".//h:section[@id='ofl-license']/h:p", NS)
    included = " ".join("".join(p.itertext()) for p in paragraphs)
    if included.split() != (ROOT / "FONT-OFL.txt").read_text(encoding="utf-8").split():
        raise ValueError("Embedded font must include the complete OFL license")
    return resources


def build(output: Path) -> None:
    resources = check_sources()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        # 最初のエントリーは非圧縮の mimetype にするルン。
        first = zipfile.ZipInfo("mimetype", date_time=ARCHIVE_DATE)
        first.compress_type = zipfile.ZIP_STORED
        first.external_attr = 0o644 << 16
        archive.writestr(first, MIMETYPE.read_bytes())
        for path in resources:
            name = path.relative_to(ROOT).as_posix()
            item = zipfile.ZipInfo(name, date_time=ARCHIVE_DATE)
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, path.read_bytes(), compresslevel=9)
    print(f"Built {output}")


def build_source_zip(output: Path) -> None:
    # distや一時ファイルを除き、ビルドに必要なソースだけを梱包するルン。
    paths = [MIMETYPE, ROOT / ".gitignore", ROOT / "README.md", ROOT / "README.en.md", ROOT / "LICENSE", ROOT / "LICENSING.md", ROOT / "cover.svg",
             ROOT / "build.py", ROOT / "test_build.py", ROOT / "generate_image_fixtures.py",
             ROOT / "generate_font_fixture.py", ROOT / "font_probe.txt", ROOT / "FONT-LICENSE.md", ROOT / "FONT-OFL.txt"]
    paths.extend(check_sources())
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        for path in sorted(paths):
            name = f"{PROJECT_NAME}/{path.relative_to(ROOT).as_posix()}"
            item = zipfile.ZipInfo(name, date_time=ARCHIVE_DATE)
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, path.read_bytes(), compresslevel=9)
    print(f"Built source archive {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build EPUB 3 and optionally run EPUBCheck")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / f"{PROJECT_NAME}.epub")
    parser.add_argument("--epubcheck", metavar="JAR", type=Path, help="EPUBCheck JAR to validate the generated EPUB")
    parser.add_argument("--source-zip", type=Path, help="Also create a ZIP of the build sources")
    args = parser.parse_args()
    try:
        build(args.output.resolve())
        if args.epubcheck:
            if not shutil.which("java"):
                raise RuntimeError("Java is not installed")
            result = subprocess.run(["java", "-jar", str(args.epubcheck.resolve()), str(args.output.resolve())], check=False)
            if result.returncode:
                return result.returncode
        if args.source_zip:
            build_source_zip(args.source_zip.resolve())
    except (OSError, ValueError, RuntimeError, ElementTree.ParseError, KeyError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

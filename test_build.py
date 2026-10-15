# SPDX-License-Identifier: MIT
"""Regression checks for the distributable typography fixtures."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="typography-build-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        for name in ("EPUB", "META-INF"):
            shutil.copytree(build.ROOT / name, self.root / name)
        for name in ("mimetype", ".gitignore", "README.md", "README.en.md", "LICENSE", "LICENSING.md", "cover.svg", "build.py", "test_build.py", "generate_image_fixtures.py", "generate_font_fixture.py", "font_probe.txt", "FONT-LICENSE.md", "FONT-OFL.txt"):
            shutil.copy2(build.ROOT / name, self.root / name)
        for name, value in {
            "ROOT": self.root,
            "MIMETYPE": self.root / "mimetype",
            "CONTAINER": self.root / "META-INF/container.xml",
            "PACKAGE": self.root / "EPUB/package.opf",
        }.items():
            context = patch.object(build, name, value)
            context.start()
            self.addCleanup(context.stop)

    def replace(self, name, before, after):
        path = self.root / "EPUB" / name
        source = path.read_text(encoding="utf-8")
        self.assertIn(before, source)
        path.write_text(source.replace(before, after, 1), encoding="utf-8")

    def test_archive_is_reproducible_and_has_exact_sources(self):
        (self.root / "EPUB/.DS_Store").write_bytes(b"Operating system metadata")
        first, second = Path(self.temp.name) / "first.epub", Path(self.temp.name) / "second.epub"
        with redirect_stdout(StringIO()):
            build.build(first)
            build.build(second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.infolist()[0].filename, "mimetype")
            self.assertEqual(archive.infolist()[0].compress_type, zipfile.ZIP_STORED)
            self.assertEqual(archive.read("mimetype"), b"application/epub+zip")
            self.assertEqual(len([name for name in archive.namelist() if '/chapter' in name]), 34)
            self.assertEqual(len([name for name in archive.namelist() if name.startswith('EPUB/images/')]), 11)
            self.assertIn("EPUB/cover.png", archive.namelist())
            self.assertIn("EPUB/colophon.xhtml", archive.namelist())
            self.assertNotIn("EPUB/.DS_Store", archive.namelist())
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (self.root / name).read_bytes())

    def test_source_zip_can_reproduce_the_epub(self):
        # 配布ZIPを別の場所へ展開し、欠落なく再ビルドできることを確かめるルン。
        archive_path = Path(self.temp.name) / "source.zip"
        (self.root / "dist").mkdir()
        (self.root / "dist/ignored.epub").write_bytes(b"not source")
        with redirect_stdout(StringIO()):
            build.build_source_zip(archive_path)
        with zipfile.ZipFile(archive_path) as archive:
            self.assertFalse(any("/dist/" in name or "__pycache__" in name for name in archive.namelist()))
            archive.extractall(Path(self.temp.name) / "unpacked")
        unpacked = Path(self.temp.name) / "unpacked" / build.PROJECT_NAME
        for name in ("build.py", "README.md", "README.en.md"):
            self.assertEqual((unpacked / name).read_bytes(), (self.root / name).read_bytes())
        import subprocess
        import sys
        rebuilt = Path(self.temp.name) / "rebuilt.epub"
        result = subprocess.run([sys.executable, "-B", str(unpacked / "build.py"), "--output", str(rebuilt)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        baseline = Path(self.temp.name) / "baseline.epub"
        with redirect_stdout(StringIO()):
            build.build(baseline)
        self.assertEqual(rebuilt.read_bytes(), baseline.read_bytes())

    def test_missing_chapter_is_rejected(self):
        (self.root / "EPUB/chapter33.xhtml").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            build.check_sources()

    def test_missing_image_is_rejected(self):
        (self.root / "EPUB/images/white-shapes.jpg").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            build.check_sources()

    def test_missing_cover_is_rejected(self):
        (self.root / "EPUB/cover.png").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            build.check_sources()

    def test_incomplete_embedded_license_is_rejected(self):
        self.replace("colophon.xhtml", 'Permission is hereby granted, free of charge', 'Permission notice removed')
        with self.assertRaisesRegex(ValueError, "complete LICENSE"):
            build.check_sources()

    def test_broken_css_font_reference_is_rejected(self):
        self.replace("font-tests.css", 'fonts/ShipporiMincho-Regular-test-subset.ttf', 'fonts/missing.ttf')
        with self.assertRaisesRegex(ValueError, "Missing"):
            build.check_sources()

    def test_incomplete_font_license_is_rejected(self):
        self.replace("colophon.xhtml", 'Copyright 2021 The Shippori Mincho Project Authors', 'Copyright notice removed')
        with self.assertRaisesRegex(ValueError, "complete OFL"):
            build.check_sources()

    def test_image_chapter_is_23(self):
        resources = build.check_sources()
        package = build.ElementTree.parse(build.PACKAGE)
        spine = [item.get("idref") for item in package.findall("opf:spine/opf:itemref", build.NS)]
        index = spine.index("c23")
        self.assertEqual(spine[index - 1:index + 2], ["c22", "c23", "c24"])
        chapter = build.ElementTree.parse(self.root / "EPUB/chapter23.xhtml")
        images = chapter.findall(".//h:img", build.NS)
        self.assertEqual(len(images), 11)
        self.assertEqual(len({image.get("src") for image in images}), 11)
        self.assertTrue(all(image.get("alt") for image in images))
        self.assertTrue(any(path.suffix == ".jpg" for path in resources))

    def test_wrong_toc_order_is_rejected(self):
        self.replace("nav.xhtml", 'href="chapter01.xhtml"', 'href="chapter02.xhtml"')
        with self.assertRaisesRegex(ValueError, "Table of contents"):
            build.check_sources()

    def test_broken_fragment_is_rejected(self):
        self.replace("chapter29.xhtml", 'href="#P001"', 'href="#P999"')
        with self.assertRaisesRegex(ValueError, "Missing fragment"):
            build.check_sources()

    def test_normalized_combining_sequence_is_rejected(self):
        self.replace("chapter33.xhtml", 'id="unicode-copy" class="probe">が／か\u3099', 'id="unicode-copy" class="probe">が／が')
        with self.assertRaisesRegex(ValueError, "normalized"):
            build.check_sources()


if __name__ == "__main__":
    unittest.main()

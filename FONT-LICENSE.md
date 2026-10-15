# Embedded font fixture

The embedded fixture is a subset of Shippori Mincho Regular, copyright 2021 The Shippori Mincho Project Authors. It is distributed under SIL Open Font License 1.1, independently of the suite's MIT License. See [FONT-OFL.txt](FONT-OFL.txt) for the copyright notice and full license. The same notice and license are available inside the EPUB at `EPUB/colophon.xhtml#font-license`.

- Project: https://github.com/fontdasu/ShipporiMincho
- Pinned source: https://github.com/google/fonts/tree/d0b2d1307ad5d6b579d627a6e5abd25952484b96/ofl/shipporimincho
- Original file: `ShipporiMincho-Regular.ttf`
- Original SHA-256: `769b5269f0f9bc6534b352c0e6bd856a566e03ff788f107191c2d835863570b2`
- Subset file: `EPUB/fonts/ShipporiMincho-Regular-test-subset.ttf`
- Subset SHA-256: `8eb90f20bc37de2586231a8c7ef86e946b39bdab165d9a9bc05a16cdd97f622f`
- Generated with HarfBuzz `hb-subset` 14.6.0.

Only the characters in `font_probe.txt` and their required layout glyphs are included. U+20BB7 and U+845B are deliberately excluded for the missing-glyph test. Outlines, metrics, vertical layout features, copyright and font names are preserved. The CSS family alias is `Typography Probe Mincho`; the internal family remains Shippori Mincho.

Normal EPUB builds use the checked-in subset and require only Python's standard library. To regenerate the font, install HarfBuzz, obtain the pinned original font and run:

```sh
python3 -B generate_font_fixture.py /path/to/ShipporiMincho-Regular.ttf
```

The generator verifies the original checksum. A different HarfBuzz release may produce a different binary; record the new version and checksum when updating it. This font is not intended as a complete Japanese font.

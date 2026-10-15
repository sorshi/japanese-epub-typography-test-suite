# Japanese EPUB Typography Test Suite

[日本語](README.md) / **English**

Japanese vertical typography tests (EPUB 3, v2 / font verification).

This reflowable EPUB test suite lets you compare Japanese EPUB readers using the same text and conditions. It covers vertical writing, ruby annotations, line-breaking rules, tate-chu-yoko, emphasis marks, illustrations, and page boundaries. The tests reference primary sources such as JLReq, CSS, and Unicode, and include case IDs and expected results. The book contains 34 test chapters (Chapters 1–34), a cover, and a colophon. Created and published by sorshi. Original content is provided under the MIT License; the embedded font is under SIL Open Font License 1.1.

## Changes in v2

Ordinary text no longer sets `font-family`, so typography tests use the reader default. Monospace code samples and the cover/colophon styles are preserved. Existing Chapter 33 is unchanged; Chapter 34 adds 14 font verification cases.

Record declared candidates, actual rendered fonts, and loading results separately. Reader preferences and Japanese alias mapping are reader policies, and different line breaks or page counts are not failures by themselves.

The embedding test includes a 34,024-byte Shippori Mincho subset under SIL Open Font License 1.1. See [provenance and regeneration](FONT-LICENSE.md) and [full license](FONT-OFL.txt). Normal builds need no additional tools or network access.

## Downloading the EPUB

Download the `japanese-epub-typography-test-suite.epub` asset from the GitHub repository's Releases page. Check the version and release notes for each release.

GitHub's `Source code (zip)` and `Source code (tar.gz)` downloads contain the source files for that release's tag. To build the EPUB, extract the archive and follow the build instructions below from the extracted directory.

## File layout

- `README.md` and `README.en.md`: Japanese documentation (the default) and its English translation
- `mimetype`: EPUB media type (the first ZIP entry, stored without compression)
- `META-INF/container.xml`: EPUB package location
- `EPUB/package.opf`: Metadata, manifest, and spine
- `EPUB/nav.xhtml`: Table of contents
- `EPUB/cover.xhtml` and `EPUB/cover.png`: Cover page and cover image for book listings
- `EPUB/colophon.xhtml`: Colophon and the full MIT License
- `EPUB/publication.css`: Styles for the cover and colophon
- `EPUB/chapter01.xhtml` through `chapter34.xhtml`: Test chapters
- `EPUB/chapter23.xhtml`: Illustration rendering, transparency, and color tests
- `EPUB/images/`: 11 PNG and JPEG images for comparing transparency, color, and proportions of white and inked pixels
- `EPUB/style.css`: Typography styles
- `generate_font_fixture.py`, `font_probe.txt`, `FONT-LICENSE.md`, `FONT-OFL.txt`: Embedded font fixture generation and licensing
- `build.py`: Builds the EPUB using only the Python standard library; optionally runs EPUBCheck
- `test_build.py`: Regression checks for packaging, links, preservation of text sequences, and reproducibility
- `generate_image_fixtures.py`: Source script for generating simple geometric images
- `cover.svg`: Editable cover artwork (1200×1600)
- `LICENSE` and `LICENSING.md`: Full MIT License and its scope

## Test coverage

Chapters 1–24 cover basic features and a combined sample. Chapter 25 explains how to use the suite and assess results. Chapters 26–33 cover boundary conditions and regression tests. Chapter 34 covers fonts. Use the case IDs to record results together with the expected rendering, reference sources, and display conditions.

| Chapters | What they test |
| --- | --- |
| 1–2 | Basic vertical writing and CSS presentation |
| 3 | Mono ruby, group ruby, and correspondence between ruby and individual base characters |
| 4–5 | Hanging punctuation: comparison of `none`, `allow-end`, and `force-end` at line ends |
| 6–7 | Tate-chu-yoko (horizontal text within vertical lines) with half-width and full-width characters |
| 8–9 | Justification of Japanese and English text |
| 10 | Different-sized glyphs and the center line in vertical writing |
| 11–13 | Position and color of emphasis marks, and their use with ruby |
| 14–15 | Two-sided ruby on the same base text (nested `ruby`) and left-side ruby |
| 16 | Comparison of `loose`, `normal`, and `strict` using identical text and line lengths |
| 17–20 | Character orientation, list markers, mixed writing directions, and glyph alignment |
| 21–22 | Repeated em dashes (U+2014), vertical kana repeat marks, and repetition symbols: connections and prevention of breaks |
| 23 | PNG and JPEG transparency, background and shape colors, thin lines, and proportions of white and inked pixels |
| 24 | Combined typography sample |
| 25 | Assessment categories, recording display conditions, and comparison procedures |
| 26 | Line-start and line-end prohibition rules, compared by character, preceding character count, and `loose` / `normal` / `strict` |
| 27 | Leader characters, dashes, and vertical kana repeat marks: unbreakable sequences and line-end boundaries |
| 28 | Mono, group, and jukugo ruby (ruby for compound words); long and short annotations; adjacency, line spacing, and wrapping |
| 29 | Long text with paragraph IDs P001–P048, headings, explicit page breaks, `widows`, and `orphans` |
| 30 | Punctuation spacing, indentation and hanging indents, paragraph-final lines, and forced line breaks |
| 31 | Mixed Japanese and Western text, numbers and units, and tate-chu-yoko with ruby and emphasis marks |
| 32 | Characters receiving emphasis marks, exclusions and symbol exceptions, left/right placement, and collisions with ruby |
| 33 | NFC and NFD, half-width voiced kana, variation selectors, supplementary-plane kanji, selection, and search |
| 34 | Reader defaults, Japanese serif aliases, named fonts, sans-serif, monospace, embedding, fallback, inheritance, and loading |

Chapter 22 includes the unvoiced vertical kana repeat mark `〳〵` (U+3033 U+3035) and its voiced counterpart `〴〵` (U+3034 U+3035). No spaces, line breaks, or HTML tags occur between the characters, so you can inspect the upper and lower glyphs and their connection in vertical text. Rendering also depends on the font in use.

## Cover and colophon

The cover comes first in the reading order and the colophon comes last. Both are accessible from the table of contents. The colophon includes the creator, creation date, version, references, license scope, and the full MIT License. The OPF also specifies the creator, publisher, rights information, and a cover image for book listings.

The editable cover artwork is an SVG made from a background color, text, and a short horizontal bar. It embeds no external images or font files. Its appearance depends on the fonts available in the viewing environment. The EPUB includes a rasterized version as `EPUB/cover.png` and uses a separate stylesheet for the cover and colophon.

## License

Copyright (c) 2026 sorshi

The source code, test text, documentation, cover, original images, and these portions of the built EPUB are provided under the MIT License. The embedded font is separately licensed under SIL Open Font License 1.1. Preserve the copyright notice and license text when redistributing them. See [LICENSE](LICENSE) for the full license and [LICENSING.md](LICENSING.md) for its scope and treatment of external materials. The full license is also included in the colophon so it remains available when the EPUB is distributed on its own.

## Illustration tests (Chapter 23)

Compare PNG and JPEG illustrations with different transparency, background colors, shape colors, line widths, and proportions of white and inked pixels. “Baseline rendering” means rendering without image correction or blending into the page background. The chapter's CSS specifies neither color transformations nor multiply blending.

| Case | Image | What to check in baseline rendering |
| --- | --- | --- |
| I23-01 | Monochrome PNG with a transparent background | The page background shows through transparent areas |
| I23-02–03 | Monochrome PNG and JPEG with white backgrounds | Opaque white backgrounds and corresponding shapes; JPEG compression differences |
| I23-04–05 | Color PNG and JPEG with white backgrounds | Distinguishable blue, red, green, and black; differences between formats |
| I23-06 | Monochrome PNG with a gray background | A background with R, G, and B each set to 230, and tonal differences in the shapes |
| I23-07 | Black to the edges, with approximately 20.1% white area at the center | Size of the central white square |
| I23-08 | Black to the edges, with approximately 5.3% white area at the center | Appearance of the smaller white square |
| I23-09 | Thin line on white, with approximately 0.293% inked pixels | A line 54 pixels wide and 2 pixels high, including its appearance when scaled down |
| I23-10 | Straight line on white, with approximately 1.085% inked pixels | Comparison with a line 100 pixels wide and 4 pixels high |
| I23-11 | Solid white PNG | An opaque white square; distinguish it from a loading failure |

Compare the images against light, colored, and dark backgrounds available in the reader. Record any image correction, color inversion, or background-blending settings used. If correction cannot be disabled, note that condition. The presence or scope of automatic correction is not a universal pass/fail criterion for all readers.

White and ink percentages refer to the number of pixels in the original image. Distinguish these proportions from screen resolution and display scale. Also test image scaling, changes to text size and viewport dimensions, and page navigation. Check aspect ratios, missing or clipped content, and the visibility of thin lines.

All images are 192×192 pixels. They use straight lines, rectangles, triangles, and squares drawn at integer coordinates, with no external assets or fonts. PNG files are generated using the Python standard library. JPEG files are converted from the same PNG files using ImageMagick. A normal EPUB build uses the included images and does not require ImageMagick.

The ImageMagick `magick` command is required only when regenerating the images.

```bash
python3 -B generate_image_fixtures.py
```

JPEG bytes may differ between ImageMagick or JPEG encoder versions. Assess rendering using the actual images being distributed.

## Building

Requires Python 3.9 or later. Run the following from the source root:

```bash
python3 build.py
```

Output: `dist/japanese-epub-typography-test-suite.epub`

You can specify a different filename or path:

```bash
python3 build.py --output /tmp/test.epub
```

To build both the EPUB and a source ZIP, for example for distribution outside GitHub:

```bash
python3 build.py --source-zip dist/japanese-epub-typography-test-suite-source.zip
```

The source ZIP includes the text, CSS, metadata, images, editable cover artwork, colophon, license files, Japanese and English READMEs, `.gitignore`, and the build, test, and image-generation scripts. It excludes `dist/`, caches, and local validation logs.

The build checks XML syntax, manifest coverage, the reading order of the cover, chapters, and colophon against the table of contents, the complete license text in the colophon, local links and fragments, duplicate IDs, and Unicode test sequences. ZIP timestamps are fixed, so identical sources and the same compression implementation produce identical archives.

Run the regression checks:

```bash
python3 -B -m unittest -v test_build.py
```

## Validation with EPUBCheck

Download and extract the distribution ZIP from the [official EPUBCheck releases](https://github.com/w3c/epubcheck/releases).

Keep `epubcheck.jar` and its dependency libraries in the directory structure supplied by the official distribution, then run:

```bash
python3 build.py --epubcheck /path/to/epubcheck/epubcheck.jar
```

You can build without `--epubcheck`, but EPUBCheck validation is **not performed** in that case.
EPUBCheck errors are propagated through the command's exit code. Java is required.
When combined with `--source-zip`, the source ZIP is created after EPUBCheck succeeds.

## Assessing rendering

Chapter 25 explains the assessment procedure. Use it together with each case's ID, expected result, and references.

- Distinguish CSS requirements, typography conventions, and implementation support or observations. Do not treat all line-break or glyph variations permitted by the specifications as failures.
- For Chapter 23, record baseline rendering separately from changes caused by background colors or image-correction settings.
- Record results as “Pass,” “Fail,” “Unsupported feature,” “Missing font support,” “Test conditions not met,” or “Not tested.”
- Record the reader, OS, and browser versions; the fonts actually used; viewport dimensions; text size; effective line spacing; and pagination mode.
- A permitted line break does not mean a break must occur at that position. Also distinguish cases where the target character never reaches the boundary.
- Test boxes specify line length using `inline-size`, which corresponds to height in vertical writing. The boxes have padding, so assess hanging punctuation against the content area's edge rather than the border.
- Chapter 29 does not prescribe a page count. Check that P001–P048 appear once each and in order, with no missing or duplicated content after relayout or forward/backward navigation.
- Feature tests do not use `!important` to forcibly override reader settings. Record any difference between the book's declarations and the effective CSS.
- Distinguish problems at normal line spacing from stress tests that deliberately use tight spacing.
- The test text can be read without JavaScript, external fonts, or external images. A network connection is needed only to open reference links.

## References

The choice of test topics was inspired by BPS's “超縦書” product introduction and its July 2013 EPUB viewer comparison table. The test text and geometric images are original; no example text, figures, screenshots, or distributed code from those references is included. Refer to the following primary sources when assessing each feature.

- [JLReq (Requirements for Japanese Text Layout)](https://www.w3.org/TR/jlreq/)
- [CSS Text Level 3](https://www.w3.org/TR/css-text-3/)
- [CSS Text Level 4 (draft)](https://www.w3.org/TR/css-text-4/)
- [CSS Ruby Level 1 (draft)](https://www.w3.org/TR/css-ruby-1/)
- [CSS Writing Modes Level 4](https://www.w3.org/TR/css-writing-modes-4/)
- [CSS Text Decoration Level 3](https://www.w3.org/TR/css-text-decor-3/)
- [CSS Fragmentation Level 3](https://www.w3.org/TR/css-break-3/)
- [Unicode UAX #29](https://www.unicode.org/reports/tr29/)
- [HTML Standard: ruby](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-ruby-element)

## Notes

This suite provides test data for observing rendering differences between EPUB readers. Passing EPUBCheck and implementing every CSS typography feature are separate matters.

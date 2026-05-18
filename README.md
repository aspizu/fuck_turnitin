# fuck_turnitin

Convert selected PDF pages to images and re-insert them, preserving the original TOC.

## Usage

```
uv run fuck_turnitin [--output OUTFILE] [--imageify RANGES] input.pdf
```

- `--imageify` — comma-separated page ranges (1-indexed) to rasterize, e.g. `1..10,11..2,4,5`
- `--output` — output path (default: `<input>_modified.pdf`)

## How it works

1. Every page is rendered to PNG via `pdf2image`
2. Specified pages are rebuilt as marginless PDFs via `reportlab` at the original page size
3. The output PDF mixes original pages untouched with the rasterized replacements
4. The original PDF outline (TOC/bookmarks) is copied as-is into the output

## Install

```bash
uv tool install git+https://github.com/aspizu/fuck_turnitin
```

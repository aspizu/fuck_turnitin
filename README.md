# fuck_turnitin

## Install

```bash
uv tool install git+https://github.com/aspizu/fuck_turnitin
```

## Usage

```bash
fuck_turnitin [--output OUTFILE] [--imageify RANGES] input.pdf
```

| Option | Description |
|--------|-------------|
| `--imageify` | Comma-separated page ranges (1-indexed) to rasterize, e.g. `1..10,11..2,4,5` |
| `--output` | Output path (default: `<input> (fucked).pdf`) |

### Examples

```bash
# Rasterize pages 3 through 7
fuck_turnitin --imageify 3..7 essay.pdf

# Rasterize specific pages
fuck_turnitin --imageify 1,5,12,14 essay.pdf

# Rasterize a whole section in reverse order
fuck_turnitin --imageify 15..20 essay.pdf --output reformatted.pdf
```

## How it works

1. Every page is rendered to a high-resolution PNG
2. Specified pages are rebuilt as clean, marginless PDFs at their original page dimensions
3. The output PDF stitches untouched vector pages together with rasterized replacements
4. The original PDF outline/table of contents is faithfully recreated in the output

The result: a valid PDF that looks identical to the human eye, but whose selected pages contain zero selectable text — just flat images.

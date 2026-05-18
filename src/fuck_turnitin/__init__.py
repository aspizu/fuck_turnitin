import argparse
import tempfile
from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def _parse_pages(value: str) -> list[int]:
    pages: list[int] = []
    for part in value.split(","):
        if ".." in part:
            start, end = part.split("..", 1)
            start, end = int(start) - 1, int(end) - 1
            step = 1 if start <= end else -1
            pages.extend(range(start, end + step, step))
        else:
            pages.append(int(part) - 1)
    return pages


def _copy_outlines(reader, writer, items, page_ref_to_idx, parent=None):
    i = 0
    while i < len(items):
        item = items[i]
        if isinstance(item, list):
            i += 1
            continue
        page_number = page_ref_to_idx.get(item.page)
        ff = item.font_format
        c = item.color
        new_parent = writer.add_outline_item(
            title=item.title or "",
            page_number=page_number,
            parent=parent,
            bold=bool(ff & 2) if ff is not None else False,
            italic=bool(ff & 1) if ff is not None else False,
            color=tuple(float(x) for x in c) if c is not None else None,
        )
        if i + 1 < len(items) and isinstance(items[i + 1], list):
            _copy_outlines(reader, writer, items[i + 1], page_ref_to_idx, parent=new_parent)
            i += 2
        else:
            i += 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="path to the input PDF file")
    parser.add_argument(
        "--output",
        type=str,
        help="path to the output PDF file (default: <input>_modified.pdf)",
    )
    parser.add_argument(
        "--imageify",
        type=_parse_pages,
        help=(
            "comma-separated page ranges (1-indexed) to convert to images"
            ", e.g. 1..10,11..2,4,5"
        ),
    )
    args = parser.parse_args()
    reader = PdfReader(args.input)
    imageify_set = set(args.imageify) if args.imageify else set()
    with tempfile.TemporaryDirectory() as tmpdir:
        images = convert_from_path(args.input)
        png_to_pdf_paths: list[str] = []
        for i, image in enumerate(images):
            png_path = Path(tmpdir) / f"page_{i:04d}.png"
            pdf_path = png_path.with_suffix(".pdf")
            image.save(png_path)
            mb = reader.pages[i].mediabox
            pw, ph = float(mb.width), float(mb.height)
            c = canvas.Canvas(str(pdf_path), pagesize=(pw, ph))
            c.drawImage(str(png_path), 0, 0, pw, ph)
            c.save()
            png_to_pdf_paths.append(str(pdf_path))
        writer = PdfWriter()
        for i in range(len(reader.pages)):
            if i in imageify_set:
                img_reader = PdfReader(png_to_pdf_paths[i])
                writer.add_page(img_reader.pages[0])
            else:
                writer.add_page(reader.pages[i])
        outline_items = reader.outline
        if outline_items:
            page_ref_to_idx = {p.indirect_reference: i for i, p in enumerate(reader.pages)}
            _copy_outlines(reader, writer, outline_items, page_ref_to_idx)
        output = args.output or str(Path(args.input).with_suffix("")) + " (fucked).pdf"
        writer.write(output)
        print(f"Saved to {output}")

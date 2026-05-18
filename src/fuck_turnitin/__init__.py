import argparse
import tempfile
from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from reportlab.pdfgen import canvas


def _parse_pages(value: str) -> list[int]:
    pages: list[int] = []
    for part in value.split(","):
        if ".." in part:
            start, end = part.split("..", 1)
            start, end = int(start), int(end)
            step = 1 if start <= end else -1
            pages.extend(range(start, end + step, step))
        else:
            pages.append(int(part))
    return pages


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
        help="comma-separated page ranges to convert to images, e.g. 0..10,11..2,4,5",
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
        outlines = reader.root_object.get("/Outlines")
        if outlines:
            writer._root_object[NameObject("/Outlines")] = outlines.clone(writer)
        output = args.output or str(Path(args.input).with_suffix("")) + " (fucked).pdf"
        writer.write(output)
        print(f"Saved to {output}")

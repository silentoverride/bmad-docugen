"""Utilities for converting PDF documents into pixel-perfect HTML templates."""

from __future__ import annotations

import dataclasses
import json
import logging
from pathlib import Path
from typing import Any, Iterable, Sequence

from .shared import MissingDependencyError

try:
    import fitz  # type: ignore  # pragma: no cover - optional dependency
except ImportError:  # pragma: no cover - optional dependency
    fitz = None  # type: ignore

try:
    from pdf2image import convert_from_path  # pragma: no cover - optional dependency
except ImportError:  # pragma: no cover - optional dependency
    convert_from_path = None  # type: ignore

LAParams = LTChar = LTImage = LTTextBox = LTTextBoxHorizontal = LTTextContainer = None  # type: ignore
extract_pages = None  # type: ignore


def _ensure_pdfminer() -> None:
    """Import pdfminer lazily so CLI help works without the dependency."""

    global extract_pages, LAParams, LTChar, LTImage, LTTextBox, LTTextBoxHorizontal, LTTextContainer

    if extract_pages is not None:
        return

    try:  # pragma: no cover - import error path is environment dependent
        from pdfminer.high_level import extract_pages as _extract_pages
        from pdfminer.layout import (
            LAParams as _LAParams,
            LTChar as _LTChar,
            LTImage as _LTImage,
            LTTextBox as _LTTextBox,
            LTTextBoxHorizontal as _LTTextBoxHorizontal,
            LTTextContainer as _LTTextContainer,
        )
    except ImportError as exc:  # pragma: no cover - import error path is environment dependent
        raise MissingDependencyError(
            "pdfminer.six is required for PDF parsing. Install the 'agentkit-pdf-html' package with its default "
            "dependencies or run 'pip install pdfminer.six'."
        ) from exc

    extract_pages = _extract_pages
    LAParams = _LAParams
    LTChar = _LTChar
    LTImage = _LTImage
    LTTextBox = _LTTextBox
    LTTextBoxHorizontal = _LTTextBoxHorizontal
    LTTextContainer = _LTTextContainer

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TextElement:
    """Represents a positioned text element extracted from a PDF page."""

    text: str
    left: float
    top: float
    width: float
    height: float
    font_size: float
    font_name: str | None = None

    def to_css(self, scale: float = 1.0) -> str:
        """Return CSS rules for the text element."""

        font_size = self.font_size * scale
        return (
            f"left: {self.left:.2f}px; top: {self.top:.2f}px;"
            f" width: {self.width:.2f}px; height: {self.height:.2f}px;"
            f" font-size: {font_size:.2f}px;"
        )


@dataclasses.dataclass
class PageLayout:
    """Container for layout information of a single PDF page."""

    width: float
    height: float
    texts: list[TextElement]
    images: list[str]


class PDFToHTMLConverter:
    """Converts PDF files into HTML and CSS templates."""

    def __init__(
        self,
        pdf_path: Path | str,
        output_dir: Path | str,
        *,
        dpi: int = 144,
        assets_subdir: str = "assets",
        laparams: LAParams | None = None,
    ) -> None:
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.assets_dir = self.output_dir / assets_subdir
        self._laparams = laparams
        self._cached_pdfminer_pages: list[Any] | None = None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def convert(self, *, text_scale: float = 1.0) -> Path:
        """Convert the PDF into HTML/CSS assets.

        Args:
            text_scale: Scaling factor applied to the computed font sizes.

        Returns:
            Path to the generated HTML file.
        """

        LOGGER.info("Starting conversion of %s", self.pdf_path)
        layouts = list(self._extract_layout())
        embedded_images = self.extract_embedded_images()
        for index, page_images in enumerate(embedded_images):
            if index < len(layouts):
                layouts[index].images = page_images
        page_images = self._render_page_images()
        html_path = self.output_dir / "index.html"
        css_path = self.output_dir / "styles.css"

        self._write_css(css_path, layouts, text_scale=text_scale)
        self._write_html(html_path, layouts, page_images)
        self._write_manifest(layouts, page_images, text_scale)

        LOGGER.info("Finished conversion -> %s", html_path)
        return html_path

    # ------------------------------------------------------------------
    # Layout extraction
    # ------------------------------------------------------------------
    def _extract_layout(self) -> Iterable[PageLayout]:
        _ensure_pdfminer()
        laparams = self._laparams or LAParams(line_margin=0.1, char_margin=2.0, word_margin=0.2)

        page_layouts = list(extract_pages(self.pdf_path, laparams=laparams))
        self._cached_pdfminer_pages = page_layouts

        for page_index, page_layout in enumerate(page_layouts):
            texts: list[TextElement] = []
            images: list[str] = []
            width = float(getattr(page_layout, "width", 0) or 0)
            height = float(getattr(page_layout, "height", 0) or 0)

            for element in page_layout:
                if isinstance(element, (LTTextContainer, LTTextBox, LTTextBoxHorizontal)):
                    texts.extend(self._extract_text_elements(element, height))

            LOGGER.debug("Page %s extracted: %s texts", page_index + 1, len(texts))
            yield PageLayout(width=width, height=height, texts=texts, images=images)

        # Leave the cached page layouts accessible for image extraction fallbacks.

    def _extract_text_elements(self, container: LTTextContainer, page_height: float) -> list[TextElement]:
        elements: list[TextElement] = []
        for text_line in container:
            if not hasattr(text_line, "_objs"):
                continue

            line_chars = [obj for obj in getattr(text_line, "_objs", []) if isinstance(obj, LTChar)]
            if not line_chars:
                continue

            x0, y0, x1, y1 = text_line.bbox
            text = text_line.get_text().replace("\n", " ").strip()
            if not text:
                continue

            font_size = sum(char.size for char in line_chars) / len(line_chars)
            font_name = line_chars[0].fontname if line_chars else None

            # Convert PDF coordinate system (origin bottom-left) to CSS (top-left)
            top = page_height - y1
            elements.append(
                TextElement(
                    text=text,
                    left=x0,
                    top=top,
                    width=x1 - x0,
                    height=y1 - y0,
                    font_size=font_size,
                    font_name=font_name,
                )
            )
        return elements

    # ------------------------------------------------------------------
    # Image extraction and rendering
    # ------------------------------------------------------------------
    def extract_embedded_images(self) -> list[list[str]]:
        """Extract all embedded images into the assets directory.

        Returns:
            List of relative asset paths for each page in the document.
        """

        if fitz is not None:
            return self._extract_images_with_pymupdf()

        LOGGER.debug("PyMuPDF is unavailable; falling back to pdfminer for image extraction.")
        return self._extract_images_with_pdfminer()

    def _extract_images_with_pymupdf(self) -> list[list[str]]:
        assert fitz is not None  # narrow type for static checkers
        embedded: list[list[str]] = []
        with fitz.open(self.pdf_path) as doc:  # type: ignore[arg-type]
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                page_images: list[str] = []
                self._clear_page_image_assets(page_index)
                for image_number, image_info in enumerate(page.get_images(full=True), start=1):
                    xref = image_info[0]
                    try:
                        base_image = doc.extract_image(xref)
                    except RuntimeError as exc:  # pragma: no cover - rare corrupt PDFs
                        LOGGER.warning("Failed to extract image %s on page %s: %s", xref, page_index + 1, exc)
                        continue

                    image_bytes = base_image.get("image")
                    if not image_bytes:
                        continue
                    extension = base_image.get("ext", "png") or "png"
                    asset_path = self.assets_dir / f"page_{page_index + 1}_image_{image_number}.{extension}"
                    with open(asset_path, "wb") as fh:
                        fh.write(image_bytes)
                    page_images.append(str(asset_path.relative_to(self.output_dir)))
                embedded.append(page_images)
        return embedded

    def _extract_images_with_pdfminer(self) -> list[list[str]]:
        _ensure_pdfminer()
        laparams = self._laparams or LAParams(line_margin=0.1, char_margin=2.0, word_margin=0.2)
        embedded: list[list[str]] = []

        page_layouts = self._cached_pdfminer_pages
        if not page_layouts:
            page_layouts = list(extract_pages(self.pdf_path, laparams=laparams))
            self._cached_pdfminer_pages = page_layouts

        for page_index, page_layout in enumerate(page_layouts):
            page_images: list[str] = []
            self._clear_page_image_assets(page_index)
            for image_number, image in enumerate(self._iter_lt_images(page_layout), start=1):
                saved = self._save_raw_image(page_index, image_number, image)
                if saved:
                    page_images.append(saved)
            embedded.append(page_images)

        return embedded

    def _iter_lt_images(self, layout_obj) -> Iterable:
        if LTImage is None:
            return
        if isinstance(layout_obj, LTImage):
            yield layout_obj
            return

        for child in getattr(layout_obj, "_objs", []) or []:
            yield from self._iter_lt_images(child)

    def _save_raw_image(self, page_index: int, image_number: int, image: LTImage) -> str | None:
        stream = getattr(image, "stream", None)
        if stream is None or not hasattr(stream, "get_data"):
            return None

        try:
            data = stream.get_data()
        except Exception as exc:  # pragma: no cover - depends on PDF contents
            LOGGER.warning("Failed to decode image %s on page %s: %s", getattr(image, "name", ""), page_index + 1, exc)
            return None

        filters: list[str] = []
        if hasattr(stream, "get_filters"):
            try:
                filters = [f.lower() for f in stream.get_filters() or []]
            except Exception:  # pragma: no cover - defensive path
                filters = []

        extension = self._resolve_image_extension(filters, image)
        asset_path = self.assets_dir / f"page_{page_index + 1}_image_{image_number}.{extension}"

        try:
            with open(asset_path, "wb") as fh:
                fh.write(data)
        except OSError as exc:  # pragma: no cover - filesystem errors are environment-specific
            LOGGER.warning("Failed to write image asset %s: %s", asset_path.name, exc)
            return None

        return str(asset_path.relative_to(self.output_dir))

    def _resolve_image_extension(self, filters: Sequence[str], image: LTImage) -> str:
        filter_set = {f.lower() for f in filters}
        if "dctdecode" in filter_set:
            return "jpg"
        if "jpxdecode" in filter_set:
            return "jp2"
        if "ccittfaxdecode" in filter_set:
            return "tiff"

        name = getattr(image, "name", "") or ""
        if "." in name:
            suffix = name.split(".")[-1].lower()
            if suffix in {"png", "jpg", "jpeg", "jp2", "tiff", "bmp", "gif"}:
                return suffix

        if filter_set:
            LOGGER.debug("Unhandled image filters %s; defaulting to png for %s", filter_set, name)
        return "png"

    def _clear_page_image_assets(self, page_index: int) -> None:
        prefix = f"page_{page_index + 1}_image_"
        for asset in self.assets_dir.glob(f"{prefix}*"):
            try:
                asset.unlink()
            except OSError:  # pragma: no cover - filesystem permissions
                LOGGER.debug("Unable to remove stale image asset %s", asset)

    def _render_page_images(self) -> list[str | None]:
        if fitz is None and convert_from_path is None:
            LOGGER.warning("Neither PyMuPDF nor pdf2image is available; background images disabled.")
            return [None] * self._page_count()

        images: List[Optional[str]] = []
        if fitz is not None:
            doc = fitz.open(self.pdf_path)
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                pix = page.get_pixmap(dpi=self.dpi)
                image_path = self.assets_dir / f"page_{page_number + 1}.png"
                pix.save(image_path)
                images.append(str(image_path.relative_to(self.output_dir)))
            return images

        assert convert_from_path is not None
        pil_images = convert_from_path(str(self.pdf_path), dpi=self.dpi)
        for page_number, image in enumerate(pil_images, start=1):
            image_path = self.assets_dir / f"page_{page_number}.png"
            image.save(image_path)
            images.append(str(image_path.relative_to(self.output_dir)))
        return images

    def _page_count(self) -> int:
        try:
            _ensure_pdfminer()
        except MissingDependencyError:
            if fitz is not None:  # pragma: no cover - optional dependency
                with fitz.open(self.pdf_path) as doc:  # type: ignore[arg-type]
                    return doc.page_count
            raise

        with open(self.pdf_path, "rb") as fh:
            return sum(1 for _ in extract_pages(fh))

    # ------------------------------------------------------------------
    # Output writers
    # ------------------------------------------------------------------
    def _write_css(self, path: Path, layouts: Sequence[PageLayout], *, text_scale: float) -> None:
        base_styles = [
            "body {",
            "  margin: 0;",
            "  background: #f2f2f2;",
            "  font-family: 'Helvetica Neue', Arial, sans-serif;",
            "}",
            ".page {",
            "  position: relative;",
            "  margin: 2rem auto;",
            "  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);",
            "  background: white;",
            "}",
            ".page__background {",
            "  position: absolute;",
            "  inset: 0;",
            "  background-size: cover;",
            "  background-position: top left;",
            "  opacity: 0.98;",
            "}",
            ".page__text {",
            "  position: absolute;",
            "  white-space: pre;",
            "  color: #000;",
            "}",
        ]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("/* Generated by Agentkit PDF to HTML converter */\n")
            fh.write("\n".join(base_styles))
            fh.write("\n")

            for index, layout in enumerate(layouts, start=1):
                fh.write(f".page--{index} {{ width: {layout.width:.2f}px; height: {layout.height:.2f}px; }}\n")
                for text_idx, text in enumerate(layout.texts, start=1):
                    fh.write(
                        f".page--{index} .text--{text_idx} {{ {text.to_css(scale=text_scale)} }}\n"
                    )

    def _write_html(
        self,
        path: Path,
        layouts: Sequence[PageLayout],
        page_images: Sequence[str | None],
    ) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n")
            fh.write("  <meta charset=\"utf-8\">\n")
            fh.write("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n")
            fh.write("  <title>PDF Conversion</title>\n")
            fh.write("  <link rel=\"stylesheet\" href=\"styles.css\">\n")
            fh.write("</head>\n<body>\n")

            for index, layout in enumerate(layouts, start=1):
                fh.write(f"  <section class=\"page page--{index}\" data-page=\"{index}\">\n")
                image_url = page_images[index - 1] if index - 1 < len(page_images) else None
                if image_url:
                    fh.write(
                        "    <div class=\"page__background\" "
                        f"style=\"background-image: url('{image_url}');\"></div>\n"
                    )
                for text_idx, text in enumerate(layout.texts, start=1):
                    safe_text = text.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    fh.write(
                        f"    <span class=\"page__text text--{text_idx}\">{safe_text}</span>\n"
                    )
                fh.write("  </section>\n")

            fh.write("</body>\n</html>\n")

    def _write_manifest(
        self,
        layouts: Sequence[PageLayout],
        page_images: Sequence[str | None],
        text_scale: float,
    ) -> None:
        manifest = {
            "pdf": str(self.pdf_path),
            "pages": [
                {
                    "width": layout.width,
                    "height": layout.height,
                    "text_count": len(layout.texts),
                    "image_count": len([img for img in layout.images if img]),
                    "images": layout.images,
                    "background": page_images[index] if index < len(page_images) else None,
                }
                for index, layout in enumerate(layouts)
            ],
            "text_scale": text_scale,
        }
        with open(self.output_dir / "manifest.json", "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)

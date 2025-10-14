"""Command line interface for Agentkit PDF to HTML conversion."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .pdf_to_html import PDFToHTMLConverter
from .shared import MissingDependencyError
from .visual_regression import TemplateRefiner, VisualRegressionTester

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert PDF to HTML5/CSS templates with regression testing.")
    parser.add_argument("pdf", type=Path, help="Path to the input PDF file.")
    parser.add_argument("output", type=Path, help="Directory where the HTML template will be written.")
    parser.add_argument("--iterations", type=int, default=3, help="Number of refinement iterations to run.")
    parser.add_argument("--no-regression", action="store_true", help="Skip the regression loop even if references exist.")
    parser.add_argument("--log-level", default="INFO", help="Python logging level (default: INFO).")
    parser.add_argument(
        "--dpi",
        type=int,
        default=144,
        help="DPI to use when rasterizing reference images for regression testing.",
    )
    return parser


def run(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        converter = PDFToHTMLConverter(args.pdf, args.output, dpi=args.dpi)
        converter.convert()
    except MissingDependencyError as exc:
        LOGGER.error("%s", exc)
        return 1

    if args.no_regression:
        LOGGER.info("Skipping regression loop as requested.")
        return 0

    # Use generated reference images when available
    manifest_path = converter.output_dir / "manifest.json"
    references: List[Path] = []
    if manifest_path.exists():
        import json

        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        for page in manifest.get("pages", []):
            reference = page.get("reference") or page.get("background")
            if reference:
                references.append(converter.output_dir / reference)

    if not references:
        LOGGER.warning("No reference images found for regression testing.")
        return 0

    try:
        tester = VisualRegressionTester()
        refiner = TemplateRefiner(converter, tester, references, max_iterations=args.iterations)
        refiner.run()
    except MissingDependencyError as exc:
        LOGGER.warning("Visual regression skipped: %s", exc)
        return 0
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())

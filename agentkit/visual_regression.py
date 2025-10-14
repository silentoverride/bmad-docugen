"""Visual regression testing helpers for Agentkit."""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

try:
    from PIL import Image, ImageChops, ImageStat
except ImportError as exc:  # pragma: no cover - optional dependency
    Image = ImageChops = ImageStat = None  # type: ignore
    PIL_IMPORT_ERROR = exc
else:
    PIL_IMPORT_ERROR = None

try:
    from playwright.sync_api import sync_playwright  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sync_playwright = None  # type: ignore

from .pdf_to_html import PDFToHTMLConverter
from .shared import MissingDependencyError

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RegressionResult:
    """Represents the outcome of a single regression comparison."""

    iteration: int
    diff_score: float
    screenshot_path: Optional[Path] = None
    diff_image_path: Optional[Path] = None


class VisualRegressionTester:
    """Renders HTML to images and measures the difference from references."""

    def __init__(self, *, viewport_width: int = 1280, viewport_height: int = 720, wait_for: float = 0.2) -> None:
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.wait_for = wait_for

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, html_path: Path, output_path: Path, *, width: int, height: int) -> Optional[Path]:
        """Render the HTML to an image using Playwright."""

        if sync_playwright is None:
            LOGGER.warning("Playwright is not available; skipping rendering step.")
            return None

        def _render() -> Optional[Path]:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": max(width, 10), "height": max(height, 10)})
                page.goto(html_path.as_uri())
                page.wait_for_timeout(int(self.wait_for * 1000))
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()
            return output_path

        return _render()

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------
    def compare(self, reference: Path, candidate: Path, diff_output: Path) -> float:
        """Return a normalized difference score between two images."""

        if Image is None or ImageChops is None or ImageStat is None:
            raise MissingDependencyError(
                "Pillow is required for image comparison. Install it with 'pip install pillow'."
            )

        ref_img = Image.open(reference).convert("RGB")
        cand_img = Image.open(candidate).convert("RGB")
        if ref_img.size != cand_img.size:
            cand_img = cand_img.resize(ref_img.size)
        diff = ImageChops.difference(ref_img, cand_img)
        diff_stat = ImageStat.Stat(diff)
        diff_score = sum(diff_stat.mean) / (255 * len(diff_stat.mean))
        # Highlight differences for debugging
        heat_map = diff.convert("L").point(lambda p: min(255, p * 8))
        heat_map_rgb = Image.merge("RGB", (heat_map, heat_map, heat_map))
        heat_map_rgb.save(diff_output)
        return diff_score


class TemplateRefiner:
    """Runs an optimization loop to minimize visual differences."""

    def __init__(
        self,
        converter: PDFToHTMLConverter,
        tester: VisualRegressionTester,
        reference_images: Sequence[Path],
        *,
        max_iterations: int = 5,
        output_dir: Optional[Path] = None,
    ) -> None:
        if Image is None:
            raise MissingDependencyError(
                "Pillow is required for regression refinement. Install it with 'pip install pillow'."
            )

        self.converter = converter
        self.tester = tester
        self.reference_images = list(reference_images)
        self.max_iterations = max_iterations
        self.output_dir = Path(output_dir) if output_dir else converter.output_dir
        self.history: List[RegressionResult] = []
        self._reference_metadata: List[Tuple[Path, int, int]] = []

        for reference in self.reference_images:
            with Image.open(reference) as img:
                self._reference_metadata.append((reference, img.width, img.height))

    def run(self) -> List[RegressionResult]:
        """Execute the refinement loop."""

        best_score = float("inf")
        best_scale = 1.0
        current_scale = 1.0
        step = 0.08
        direction = 1

        for iteration in range(1, self.max_iterations + 1):
            LOGGER.info("Refinement iteration %s (scale=%.3f)", iteration, current_scale)
            html_path = self.converter.convert(text_scale=current_scale)

            iteration_dir = self.output_dir / f"iteration_{iteration}"
            iteration_dir.mkdir(exist_ok=True)

            aggregate_score = 0.0
            comparisons = 0
            for page_number, (reference, width, height) in enumerate(self._reference_metadata, start=1):
                screenshot = iteration_dir / f"page_{page_number}.png"
                diff_output = iteration_dir / f"page_{page_number}_diff.png"
                rendered = self.tester.render(html_path, screenshot, width=width, height=height)

                # If Playwright isn't available, skip comparisons but keep record
                if rendered is None:
                    LOGGER.warning("Skipping regression comparison (rendering unavailable).")
                    result = RegressionResult(iteration=iteration, diff_score=float("nan"), screenshot_path=None, diff_image_path=None)
                    self.history.append(result)
                    continue

                diff_score = self.tester.compare(reference, screenshot, diff_output)
                aggregate_score += diff_score
                comparisons += 1
                self.history.append(
                    RegressionResult(
                        iteration=iteration,
                        diff_score=diff_score,
                        screenshot_path=screenshot,
                        diff_image_path=diff_output,
                    )
                )

            if comparisons:
                mean_score = aggregate_score / comparisons
                LOGGER.info("Iteration %s mean diff: %.4f", iteration, mean_score)
                if mean_score < best_score:
                    best_score = mean_score
                    best_scale = current_scale
                else:
                    direction *= -1
                    step *= 0.5
                current_scale = max(0.5, min(1.5, current_scale + direction * step))
            else:
                LOGGER.info("No comparisons performed; terminating refinement loop early.")
                break

        if best_scale != current_scale:
            LOGGER.info("Rendering final output with best scale %.3f", best_scale)
            self.converter.convert(text_scale=best_scale)

        return self.history

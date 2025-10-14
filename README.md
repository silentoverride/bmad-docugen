# Agentkit PDF to HTML Utility

This project provides a command line utility that transforms PDF documents into pixel-perfect HTML5/CSS templates. It also features an optional visual regression testing loop that evaluates and iteratively refines the output so that it more closely matches the original PDF.

## Features

- Extracts positioned text layers from PDFs using `pdfminer.six` and renders them as absolutely positioned HTML elements.
- Optionally rasterizes each page with [PyMuPDF](https://pymupdf.readthedocs.io/) or [pdf2image](https://github.com/Belval/pdf2image) to create high-fidelity reference images for regression testing (they are not embedded in the HTML output).
- Saves every embedded image from the PDF into an `assets/` directory for use inside the generated template.
- Infers font families, weights, and styles from the PDF metadata to better match original typography.
- Produces a clean HTML template with inline styles and a manifest describing the conversion output.
- Includes a visual regression workflow powered by [Playwright](https://playwright.dev/python/) that screenshots the generated HTML and compares it to the PDF rasterization using perceptual difference metrics.
- Automatically tunes font scaling over multiple iterations to minimize the detected visual differences.

## Installation

Create and activate a Python 3.10+ virtual environment, then install the package in editable mode:

```bash
pip install -e .
```

The converter loads heavy dependencies lazily so that `agentkit --help` works even before everything is installed. The actual
conversion requires [`pdfminer.six`](https://github.com/pdfminer/pdfminer.six); the command will exit with an informative
message if it is missing.

To enable reference rendering you will also need the optional dependencies and the relevant system packages (such as Poppler for `pdf2image`). You can install everything with:

```bash
pip install -e .[render]
```

Finally, ensure that Playwright browsers are installed:

```bash
playwright install chromium
```

## Usage

```bash
agentkit path/to/input.pdf output-directory
```

The command will generate `index.html`, a manifest file, and any extracted assets in the chosen output directory. The HTML file includes an inline `<style>` block so no separate stylesheet is required, and it renders text directly on a blank canvas without using page-sized background images. After the initial conversion the visual regression loop will run automatically when reference page images are available, updating the template when improvements are detected.

### Extracting embedded images only

If you need direct access to the images embedded inside the PDF, the converter exposes an `extract_embedded_images()` helper:

```python
from pathlib import Path
from agentkit import PDFToHTMLConverter

converter = PDFToHTMLConverter(Path("input.pdf"), Path("output"))
image_paths = converter.extract_embedded_images()
# image_paths is a list of lists keyed by page -> ["assets/page_1_image_1.jpg", ...]
```

Each call overwrites the corresponding files in the `assets/` folder so the paths always reflect the most recent extraction. Images that cover most of a page (such as a flattened background) are skipped so that only smaller assets like logos are emitted.

### Flags

- `--iterations` – Number of refinement iterations to perform (default: 3).
- `--no-regression` – Skip the regression loop entirely.
- `--dpi` – Override the rasterization DPI used for the regression reference images.
- `--log-level` – Adjust logging verbosity (defaults to `INFO`).

## Visual Regression Output

Each refinement iteration stores screenshots and heatmap visualizations of the differences inside `iteration_<n>` directories. The mean difference score per iteration is logged to the console, making it easy to monitor convergence.

## Development

Run static checks and formatters as needed. Tests are not included, but you can lint the project with `ruff` or run type checks with `mypy` if desired.

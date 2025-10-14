"""Agentkit utility package for PDF to HTML conversion with visual regression."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["PDFToHTMLConverter", "VisualRegressionTester", "TemplateRefiner"]


def __getattr__(name: str) -> Any:  # pragma: no cover - trivial delegation
    if name == "PDFToHTMLConverter":
        return getattr(import_module("agentkit.pdf_to_html"), name)
    if name in {"VisualRegressionTester", "TemplateRefiner"}:
        return getattr(import_module("agentkit.visual_regression"), name)
    raise AttributeError(name)

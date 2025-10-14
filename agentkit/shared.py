"""Shared helpers for optional dependency management."""

from __future__ import annotations


class MissingDependencyError(RuntimeError):
    """Raised when a required runtime dependency is unavailable."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:  # pragma: no cover - trivial delegation
        return self.message

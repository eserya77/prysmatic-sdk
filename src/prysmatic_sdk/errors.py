"""Typed SDK exceptions."""

from __future__ import annotations

from typing import Any


class PrysmaticError(Exception):
    """Base class for all SDK errors."""


class PrysmaticAPIError(PrysmaticError):
    """REST API error returned by Prysmatic."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        detail: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class UnauthorizedError(PrysmaticAPIError):
    """The API key is missing, invalid, or expired."""


class InsufficientCreditsError(PrysmaticAPIError):
    """The account cannot pay for the requested API call or stream payload."""


class RateLimitedError(PrysmaticAPIError):
    """The API rejected the request because the caller is rate limited."""


class NotFoundError(PrysmaticAPIError):
    """A requested resource does not exist."""


class WalletNotFoundError(NotFoundError):
    """The requested wallet alias does not exist."""


class StreamError(PrysmaticError):
    """WebSocket stream error."""


class StreamSupersededError(StreamError):
    """Another connection using the same API key replaced this stream."""

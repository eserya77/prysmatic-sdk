"""Shared client helpers."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx

from .errors import (
    InsufficientCreditsError,
    NotFoundError,
    PrysmaticAPIError,
    RateLimitedError,
    UnauthorizedError,
    WalletNotFoundError,
)

DEFAULT_BASE_URL = "https://api.prysmatic-sol.xyz"


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def derive_ws_url(base_url: str) -> str:
    parsed = urlparse(normalize_base_url(base_url))
    scheme = "wss" if parsed.scheme == "https" else "ws"
    path = parsed.path.rstrip("/") + "/ws"
    return urlunparse((scheme, parsed.netloc, path, "", "", ""))


def auth_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "prysmatic-sdk-python/0.1.0",
    }


def response_detail(response: httpx.Response) -> Any:
    try:
        data = response.json()
    except ValueError:
        return response.text
    if isinstance(data, dict) and "detail" in data:
        return data["detail"]
    return data


def raise_for_api_error(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    detail = response_detail(response)
    message = str(detail) if detail else response.reason_phrase
    kwargs = {"status_code": response.status_code, "detail": detail}

    if response.status_code == 401:
        raise UnauthorizedError(message, **kwargs)
    if response.status_code == 402:
        raise InsufficientCreditsError(message, **kwargs)
    if response.status_code == 404 and detail == "wallet_not_found":
        raise WalletNotFoundError(message, **kwargs)
    if response.status_code == 404:
        raise NotFoundError(message, **kwargs)
    if response.status_code == 429:
        raise RateLimitedError(message, **kwargs)

    raise PrysmaticAPIError(message, **kwargs)

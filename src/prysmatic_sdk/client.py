"""Synchronous REST client."""

from __future__ import annotations

from typing import Any

import httpx

from ._base import (
    DEFAULT_BASE_URL,
    auth_headers,
    normalize_base_url,
    raise_for_api_error,
)
from .resources.tokens import TokensResource
from .resources.wallets import WalletsResource


class PrysmaticClient:
    """Synchronous client for Prysmatic REST endpoints."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = 20.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = normalize_base_url(base_url)
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)
        self.wallets = WalletsResource(self)
        self.tokens = TokensResource(self)

    def __enter__(self) -> "PrysmaticClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        response = self._client.get(
            f"{self.base_url}{path}",
            params=params,
            headers=auth_headers(self.api_key),
        )
        raise_for_api_error(response)
        return response.json()

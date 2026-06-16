"""Asynchronous REST and WebSocket client."""

from __future__ import annotations

from typing import Any

import httpx

from ._base import (
    DEFAULT_BASE_URL,
    auth_headers,
    derive_ws_url,
    normalize_base_url,
    raise_for_api_error,
)
from .resources.tokens import AsyncTokensResource
from .resources.wallets import AsyncWalletsResource
from .stream import StreamResource


class AsyncPrysmaticClient:
    """Async client for Prysmatic REST and WebSocket endpoints."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        ws_url: str | None = None,
        timeout: float | httpx.Timeout = 20.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = normalize_base_url(base_url)
        self.ws_url = ws_url or derive_ws_url(self.base_url)
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self.wallets = AsyncWalletsResource(self)
        self.tokens = AsyncTokensResource(self)
        self.stream = StreamResource(self.api_key, self.ws_url)

    async def __aenter__(self) -> "AsyncPrysmaticClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        response = await self._client.get(
            f"{self.base_url}{path}",
            params=params,
            headers=auth_headers(self.api_key),
        )
        raise_for_api_error(response)
        return response.json()

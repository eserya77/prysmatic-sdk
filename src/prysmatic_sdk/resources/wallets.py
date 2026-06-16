"""Wallet endpoint resources."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import (
    WalletHoldingsResponse,
    WalletItem,
    WalletsResponse,
)

from ._transport import AsyncTransport, SyncTransport


class WalletsResource:
    """Synchronous wallet API group."""

    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def list(self, *, page: int = 1) -> WalletsResponse:
        data = self._client.get("/wallets", params={"page": page})
        return WalletsResponse.model_validate(data)

    def iter_all(self) -> Iterator[WalletItem]:
        page = 1
        while True:
            batch = self.list(page=page)
            yield from batch.items
            if not batch.has_more:
                return
            page += 1

    def metrics(self, alias: str) -> WalletItem:
        data = self._client.get(f"/wallets/{alias}/metrics")
        return WalletItem.model_validate(data)

    def holdings(self, alias: str) -> WalletHoldingsResponse:
        data = self._client.get(f"/wallets/{alias}/holdings")
        return WalletHoldingsResponse.model_validate(data)


class AsyncWalletsResource:
    """Asynchronous wallet API group."""

    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def list(self, *, page: int = 1) -> WalletsResponse:
        data = await self._client.get("/wallets", params={"page": page})
        return WalletsResponse.model_validate(data)

    async def iter_all(self) -> AsyncIterator[WalletItem]:
        page = 1
        while True:
            batch = await self.list(page=page)
            for item in batch.items:
                yield item
            if not batch.has_more:
                return
            page += 1

    async def metrics(self, alias: str) -> WalletItem:
        data = await self._client.get(f"/wallets/{alias}/metrics")
        return WalletItem.model_validate(data)

    async def holdings(self, alias: str) -> WalletHoldingsResponse:
        data = await self._client.get(f"/wallets/{alias}/holdings")
        return WalletHoldingsResponse.model_validate(data)

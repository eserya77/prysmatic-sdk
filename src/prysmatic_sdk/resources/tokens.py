"""Token endpoint resources."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import (
    SwapItem,
    TokenAggregatesResponse,
    TokenHeldItem,
    TokenSwapsResponse,
    TokensHeldResponse,
)

from ._transport import AsyncTransport, SyncTransport


class TokensResource:
    """Synchronous token API group."""

    def __init__(self, client: SyncTransport) -> None:
        self._client = client

    def held(self, *, min_wallets: int = 2, page: int = 1) -> TokensHeldResponse:
        data = self._client.get(
            "/tokens/held",
            params={"min_wallets": min_wallets, "page": page},
        )
        return TokensHeldResponse.model_validate(data)

    def iter_held(self, *, min_wallets: int = 2) -> Iterator[TokenHeldItem]:
        page = 1
        while True:
            batch = self.held(min_wallets=min_wallets, page=page)
            yield from batch.items
            if not batch.has_more:
                return
            page += 1

    def swaps(
        self,
        mint: str,
        *,
        limit: int = 100,
        cursor: str | None = None,
    ) -> TokenSwapsResponse:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._client.get(
            f"/tokens/{mint}/swaps",
            params=params,
        )
        return TokenSwapsResponse.model_validate(data)

    def iter_swaps(self, mint: str, *, limit: int = 100) -> Iterator[SwapItem]:
        cursor: str | None = None
        while True:
            batch = self.swaps(mint, limit=limit, cursor=cursor)
            yield from batch.items
            if not batch.has_more or not batch.next_cursor:
                return
            cursor = batch.next_cursor

    def wallet_aggregates(self, mint: str) -> TokenAggregatesResponse:
        data = self._client.get(f"/tokens/{mint}/wallet-aggregates")
        return TokenAggregatesResponse.model_validate(data)


class AsyncTokensResource:
    """Asynchronous token API group."""

    def __init__(self, client: AsyncTransport) -> None:
        self._client = client

    async def held(
        self,
        *,
        min_wallets: int = 2,
        page: int = 1,
    ) -> TokensHeldResponse:
        data = await self._client.get(
            "/tokens/held",
            params={"min_wallets": min_wallets, "page": page},
        )
        return TokensHeldResponse.model_validate(data)

    async def iter_held(
        self,
        *,
        min_wallets: int = 2,
    ) -> AsyncIterator[TokenHeldItem]:
        page = 1
        while True:
            batch = await self.held(min_wallets=min_wallets, page=page)
            for item in batch.items:
                yield item
            if not batch.has_more:
                return
            page += 1

    async def swaps(
        self,
        mint: str,
        *,
        limit: int = 100,
        cursor: str | None = None,
    ) -> TokenSwapsResponse:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = await self._client.get(
            f"/tokens/{mint}/swaps",
            params=params,
        )
        return TokenSwapsResponse.model_validate(data)

    async def iter_swaps(
        self,
        mint: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[SwapItem]:
        cursor: str | None = None
        while True:
            batch = await self.swaps(mint, limit=limit, cursor=cursor)
            for item in batch.items:
                yield item
            if not batch.has_more or not batch.next_cursor:
                return
            cursor = batch.next_cursor

    async def wallet_aggregates(self, mint: str) -> TokenAggregatesResponse:
        data = await self._client.get(f"/tokens/{mint}/wallet-aggregates")
        return TokenAggregatesResponse.model_validate(data)

"""Token endpoint resources."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import (
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
        aggregate: bool = False,
        tracked_only: bool = True,
    ) -> TokenSwapsResponse | TokenAggregatesResponse:
        data = self._client.get(
            f"/tokens/{mint}/swaps",
            params={"aggregate": aggregate, "tracked_only": tracked_only},
        )
        if aggregate:
            return TokenAggregatesResponse.model_validate(data)
        return TokenSwapsResponse.model_validate(data)


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
        aggregate: bool = False,
        tracked_only: bool = True,
    ) -> TokenSwapsResponse | TokenAggregatesResponse:
        data = await self._client.get(
            f"/tokens/{mint}/swaps",
            params={"aggregate": aggregate, "tracked_only": tracked_only},
        )
        if aggregate:
            return TokenAggregatesResponse.model_validate(data)
        return TokenSwapsResponse.model_validate(data)

"""Internal protocols used by endpoint resources."""

from __future__ import annotations

from typing import Any, Protocol


class SyncTransport(Protocol):
    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any: ...


class AsyncTransport(Protocol):
    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any: ...

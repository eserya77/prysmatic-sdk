"""Async WebSocket streaming helpers."""

from __future__ import annotations

import asyncio
import inspect
import json
import random
from collections.abc import AsyncGenerator, Sequence
from typing import Any

import websockets

from .errors import (
    InsufficientCreditsError,
    StreamError,
    StreamSupersededError,
)
from .models import TradeMessage


class StreamResource:
    def __init__(self, api_key: str, ws_url: str) -> None:
        self._api_key = api_key
        self._ws_url = ws_url

    async def trades(
        self,
        *,
        wallets: Sequence[str] | None = None,
        reconnect: bool = True,
        max_backoff: float = 60.0,
    ) -> AsyncGenerator[TradeMessage, None]:
        """Yield live tracked-wallet trade messages.

        Reconnects with exponential backoff unless the server says the balance is
        exhausted or the connection was superseded by another session.
        """
        delay = 1.0
        while True:
            try:
                async with websockets.connect(
                    self._ws_url,
                    **_authorization_header_kwargs(self._api_key),
                    ping_interval=None,
                ) as ws:
                    await ws.send(json.dumps(_subscribe_payload(wallets)))
                    delay = 1.0
                    async for raw in ws:
                        message = _decode_message(raw)
                        kind = message.get("type")
                        if kind == "ping":
                            continue
                        if kind == "balance_exhausted":
                            raise InsufficientCreditsError(
                                "balance_exhausted",
                                status_code=None,
                                detail=message,
                            )
                        if kind == "superseded":
                            raise StreamSupersededError(
                                "stream superseded by another connection"
                            )
                        if message.get("channel") == "trades":
                            yield TradeMessage.model_validate(message)
            except (InsufficientCreditsError, StreamSupersededError):
                raise
            except Exception as exc:
                if not reconnect:
                    raise StreamError(str(exc)) from exc
                await asyncio.sleep(delay + random.uniform(0, delay))
                delay = min(delay * 2, max_backoff)


def _subscribe_payload(wallets: Sequence[str] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "action": "subscribe",
        "channels": ["trades"],
    }
    if wallets:
        payload["wallets"] = list(wallets)
    return payload


def _authorization_header_kwargs(api_key: str) -> dict[str, dict[str, str]]:
    headers = {"Authorization": f"Bearer {api_key}"}
    parameters = inspect.signature(websockets.connect).parameters
    if "additional_headers" in parameters:
        return {"additional_headers": headers}
    return {"extra_headers": headers}


def _decode_message(raw: str | bytes) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise StreamError("received non-json websocket payload") from exc
    if not isinstance(data, dict):
        raise StreamError("received non-object websocket payload")
    return data

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest
import websockets

from prysmatic_sdk.errors import StreamError
from prysmatic_sdk.stream import (
    StreamResource,
    _authorization_header_kwargs,
    _decode_message,
    _subscribe_payload,
)


def test_subscribe_payload_with_wallet_filter() -> None:
    assert _subscribe_payload(["W12", "W37"]) == {
        "action": "subscribe",
        "channels": ["trades"],
        "wallets": ["W12", "W37"],
    }


def test_subscribe_payload_without_wallet_filter() -> None:
    assert _subscribe_payload(None) == {
        "action": "subscribe",
        "channels": ["trades"],
    }


def test_decode_message_rejects_invalid_payloads() -> None:
    with pytest.raises(StreamError):
        _decode_message("not json")

    with pytest.raises(StreamError):
        _decode_message("[1, 2, 3]")


def test_authorization_header_kwargs() -> None:
    kwargs = _authorization_header_kwargs("test-key")
    headers = kwargs.get("additional_headers") or kwargs.get("extra_headers")
    assert headers == {"Authorization": "Bearer test-key"}


def test_trade_stream_reads_from_websocket_server() -> None:
    async def run() -> None:
        received_subscriptions: list[dict[str, Any]] = []

        async def handler(ws: Any) -> None:
            assert ws.request_headers["Authorization"] == "Bearer test-key"
            raw = await ws.recv()
            received_subscriptions.append(json.loads(raw))
            await ws.send(json.dumps({"type": "ping"}))
            await ws.send(
                json.dumps(
                    {
                        "channel": "trades",
                        "data": {
                            "block_time": 1781404511,
                            "wallet": "W12",
                            "side": "buy",
                            "mint": "Mint111",
                            "token_amount": "20415437641764",
                            "decimals": 6,
                            "sol_amount": 4.063765757,
                            "quote_mint": (
                                "So11111111111111111111111111111111111111112"
                            ),
                            "quote_amount": "4063765757",
                            "program": "pump.fun",
                        },
                    }
                )
            )
            await ws.close()

        server = await websockets.serve(
            handler,
            "127.0.0.1",
            0,
        )
        try:
            socket = next(iter(server.sockets))
            host, port = socket.getsockname()[:2]
            stream = StreamResource("test-key", f"ws://{host}:{port}")
            trades = stream.trades(wallets=["W12"], reconnect=False)
            trade = await anext(trades)
            await trades.aclose()
        finally:
            server.close()
            await server.wait_closed()

        assert received_subscriptions == [
            {"action": "subscribe", "channels": ["trades"], "wallets": ["W12"]}
        ]
        assert trade.data.wallet == "W12"
        assert trade.data.side == "buy"
        assert trade.data.mint == "Mint111"

    asyncio.run(run())

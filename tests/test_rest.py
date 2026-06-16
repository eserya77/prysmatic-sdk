from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest

from prysmatic_sdk import (
    AsyncPrysmaticClient,
    InsufficientCreditsError,
    PrysmaticClient,
    TokenAggregatesResponse,
    TokenSwapsResponse,
    UnauthorizedError,
    WalletNotFoundError,
)


def wallet_item(alias: str = "W12") -> dict[str, Any]:
    return {
        "identity": {
            "wallet": alias,
            "tracked": True,
            "score": 82.4,
            "status": "scored",
        },
        "pnl": {
            "sol_balance": 12.5,
            "pnl_sol": 40.2,
            "sol_bought": 120.0,
            "sol_sold": 160.2,
            "sol_invested_open": 8.1,
            "unrealized_token_count": 3,
        },
        "activity": {
            "total_trades": 318,
            "buys": 170,
            "sells": 148,
            "transfers_in": 5,
            "transfers_out": 2,
            "sol_received": 0.0,
            "sol_sent": 0.0,
            "unique_tokens_traded": 96,
        },
        "behavior": {
            "winrate": 61.0,
            "loserate": 39.0,
            "avg_holding_time": 5400,
            "avg_time_to_almost_full_exit": 7200,
            "avg_buy_amount": 0.7,
            "avg_sell_amount": 1.1,
            "quick_sells": 12,
            "sold_more_than_bought": 8,
            "active_times": [{"hour_utc": 14, "tx_count": 40}],
        },
        "computed_at": 1781450000,
    }


def wallets_page(page: int, *, has_more: bool = False) -> dict[str, Any]:
    return {
        "page": page,
        "page_size": 25,
        "total": 2,
        "has_more": has_more,
        "items": [wallet_item(f"W{page}")],
    }


def holdings_response(alias: str = "W12") -> dict[str, Any]:
    return {
        "wallet": alias,
        "tokens": [
            {
                "token": {"address": "Mint111", "decimals": 6},
                "position": {
                    "balance": 10.5,
                    "tokens_acquired": 20.0,
                    "tokens_held": 10.5,
                    "sol_invested": 2.5,
                },
                "timing": {
                    "first_activity_at": 1781380000,
                    "last_activity_at": 1781450000,
                    "holding_time": 70000,
                },
            }
        ],
    }


def tokens_held_response() -> dict[str, Any]:
    return {
        "min_wallets": 2,
        "page": 1,
        "page_size": 25,
        "total": 1,
        "has_more": False,
        "items": [
            {
                "token": {"address": "Mint111", "decimals": 6},
                "holders": {"wallet_count": 2, "wallets": ["W1", "W2"]},
                "aggregate": {"tokens_held": 100.0, "sol_invested": 5.0},
            }
        ],
    }


def token_swaps_response() -> dict[str, Any]:
    return {
        "mint": "Mint111",
        "count": 1,
        "items": [
            {
                "block_time": 1781450361,
                "wallet": "W72",
                "side": "sell",
                "base_mint": "Mint111",
                "base_amount": "6280118271393",
                "base_decimals": 6,
                "quote_mint": "So11111111111111111111111111111111111111112",
                "quote_amount": "9311208742",
                "program": "pump.fun",
                "confidence": "high",
                "quote_mismatch": False,
            }
        ],
    }


def token_aggregates_response() -> dict[str, Any]:
    return {
        "mint": "Mint111",
        "tracked_wallets": 1,
        "wallets": [
            {
                "wallet": "W221",
                "alias": "W221",
                "buys": 2,
                "sells": 1,
                "base_bought": "23606614317783",
                "base_sold": "21460559039733",
                "base_net": "2146055278050",
                "sol_in": 8.69,
                "sol_out": 5.63,
                "pct_held": 0.0909,
                "first_buy_time": 1781448342,
                "last_trade_time": 1781448742,
                "entry_mcap": 51230.0,
            }
        ],
    }


def make_sync_client(handler: httpx.MockTransport) -> PrysmaticClient:
    http = httpx.Client(transport=handler)
    return PrysmaticClient("test-key", base_url="https://api.test", client=http)


def test_sync_rest_resources_parse_models_and_send_auth_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-key"
        assert request.headers["accept"] == "application/json"

        if request.url.path == "/wallets":
            page = int(request.url.params["page"])
            return httpx.Response(200, json=wallets_page(page, has_more=page == 1))
        if request.url.path == "/wallets/W12/metrics":
            return httpx.Response(200, json=wallet_item())
        if request.url.path == "/wallets/W12/holdings":
            return httpx.Response(200, json=holdings_response())
        if request.url.path == "/tokens/held":
            assert request.url.params["min_wallets"] == "2"
            return httpx.Response(200, json=tokens_held_response())
        if request.url.path == "/tokens/Mint111/swaps":
            if request.url.params["aggregate"] == "true":
                return httpx.Response(200, json=token_aggregates_response())
            return httpx.Response(200, json=token_swaps_response())
        raise AssertionError(f"unexpected request: {request.url}")

    client = make_sync_client(httpx.MockTransport(handler))

    wallets = client.wallets.list()
    assert wallets.items[0].identity.wallet == "W1"
    assert [item.identity.wallet for item in client.wallets.iter_all()] == ["W1", "W2"]
    assert client.wallets.metrics("W12").behavior.winrate == 61.0
    assert client.wallets.holdings("W12").tokens[0].token.address == "Mint111"
    assert client.tokens.held().items[0].holders.wallet_count == 2
    swaps = client.tokens.swaps("Mint111")
    aggregate = client.tokens.swaps("Mint111", aggregate=True)
    assert isinstance(swaps, TokenSwapsResponse)
    assert isinstance(aggregate, TokenAggregatesResponse)
    assert swaps.count == 1
    assert aggregate.tracked_wallets == 1


@pytest.mark.parametrize(
    ("status_code", "detail", "expected"),
    [
        (401, "invalid_api_key", UnauthorizedError),
        (402, "insufficient_credits", InsufficientCreditsError),
        (404, "wallet_not_found", WalletNotFoundError),
    ],
)
def test_sync_error_mapping(
    status_code: int,
    detail: str,
    expected: type[Exception],
) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": detail})

    client = make_sync_client(httpx.MockTransport(handler))

    with pytest.raises(expected):
        client.wallets.list()


def test_async_rest_resources_parse_models() -> None:
    async def run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/wallets":
                page = int(request.url.params["page"])
                return httpx.Response(200, json=wallets_page(page))
            if request.url.path == "/tokens/Mint111/swaps":
                return httpx.Response(200, json=token_aggregates_response())
            raise AssertionError(f"unexpected request: {request.url}")

        http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        async with AsyncPrysmaticClient(
            "test-key",
            base_url="https://api.test",
            client=http,
        ) as client:
            wallets = await client.wallets.list()
            flow = await client.tokens.swaps("Mint111", aggregate=True)

        assert wallets.items[0].identity.wallet == "W1"
        assert isinstance(flow, TokenAggregatesResponse)
        assert flow.wallets[0].wallet == "W221"

    asyncio.run(run())

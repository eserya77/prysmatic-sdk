"""Pydantic response models for Prysmatic API payloads."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class SDKModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class WalletIdentity(SDKModel):
    wallet: str
    tracked: bool
    score: float | None = None
    status: str | None = None


class WalletPnl(SDKModel):
    sol_balance: float | None = None
    pnl_sol: float | None = None
    sol_bought: float | None = None
    sol_sold: float | None = None
    sol_invested_open: float | None = None
    unrealized_token_count: int | None = None


class WalletActivity(SDKModel):
    total_trades: int | None = None
    buys: int | None = None
    sells: int | None = None
    transfers_in: int | None = None
    transfers_out: int | None = None
    sol_received: float | None = None
    sol_sent: float | None = None
    unique_tokens_traded: int | None = None


class WalletBehavior(SDKModel):
    winrate: float | None = None
    loserate: float | None = None
    avg_holding_time: float | None = None
    avg_time_to_almost_full_exit: float | None = None
    avg_buy_amount: float | None = None
    avg_sell_amount: float | None = None
    quick_sells: int | None = None
    sold_more_than_bought: int | None = None
    active_times: Any = None


class WalletItem(SDKModel):
    identity: WalletIdentity
    pnl: WalletPnl
    activity: WalletActivity
    behavior: WalletBehavior
    computed_at: int | None = None


class WalletsResponse(SDKModel):
    page: int
    page_size: int
    total: int
    has_more: bool
    items: list[WalletItem]


class HoldingToken(SDKModel):
    address: str
    decimals: int | None = None


class HoldingPosition(SDKModel):
    balance: float
    tokens_acquired: float
    tokens_held: float
    sol_invested: float


class HoldingTiming(SDKModel):
    first_activity_at: int | None = None
    last_activity_at: int | None = None
    holding_time: int | None = None


class WalletHoldingItem(SDKModel):
    token: HoldingToken
    position: HoldingPosition
    timing: HoldingTiming


class WalletHoldingsResponse(SDKModel):
    wallet: str
    tokens: list[WalletHoldingItem]


class HeldHolders(SDKModel):
    wallet_count: int
    wallets: list[str]


class HeldAggregate(SDKModel):
    tokens_held: float
    sol_invested: float


class TokenHeldItem(SDKModel):
    token: HoldingToken
    holders: HeldHolders
    aggregate: HeldAggregate


class TokensHeldResponse(SDKModel):
    min_wallets: int
    page: int
    page_size: int
    total: int
    has_more: bool
    items: list[TokenHeldItem]


class SwapItem(SDKModel):
    block_time: int | None = None
    wallet: str
    side: Literal["buy", "sell"] | str
    base_mint: str
    base_symbol: str | None = None
    base_amount: str
    base_decimals: int | None = None
    quote_mint: str | None = None
    quote_amount: str | None = None
    program: str | None = None
    confidence: str | None = None
    quote_mismatch: bool


class TokenSwapsResponse(SDKModel):
    mint: str
    count: int
    limit: int
    has_more: bool
    next_cursor: str | None = None
    items: list[SwapItem]


class TokenWalletAggregate(SDKModel):
    wallet: str
    alias: str | None = None
    buys: int
    sells: int
    base_bought: str
    base_sold: str
    base_net: str
    sol_in: float
    sol_out: float
    pct_held: float
    first_buy_time: int | None = None
    last_trade_time: int | None = None
    entry_mcap: float | None = None


class TokenAggregatesResponse(SDKModel):
    mint: str
    tracked_wallets: int
    wallets: list[TokenWalletAggregate]


class TradeData(SDKModel):
    block_time: int | None = None
    wallet: str
    side: Literal["buy", "sell"] | str
    mint: str
    token_amount: str
    decimals: int | None = None
    sol_amount: float | None = None
    quote_mint: str | None = None
    quote_amount: str | None = None
    program: str | None = None


class TradeMessage(SDKModel):
    channel: Literal["trades"] | str
    data: TradeData

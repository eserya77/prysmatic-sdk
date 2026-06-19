# Prysmatic Python SDK

Python client for the Prysmatic wallet intelligence API.

The SDK exposes Prysmatic as composable data primitives for builders:

- tracked wallet metrics and holdings
- token co-holding discovery
- token-level tracked-wallet swap flows
- live tracked-wallet trades over WebSocket

Wallets are represented as Prysmatic aliases such as `W12`. The SDK does not expose
real tracked-wallet addresses.

## Install

From the SDK repo:

```bash
python -m pip install -e .
```

When published:

```bash
python -m pip install prysmatic-sdk
```

## Repository layout

```text
src/prysmatic_sdk/
  client.py              # synchronous top-level REST client
  async_client.py        # asynchronous REST client + stream entrypoint
  resources/             # endpoint groups: wallets, tokens
  stream.py              # WebSocket live trade iterator
  models.py              # typed Pydantic response models
  errors.py              # typed SDK exceptions
  _base.py               # internal HTTP helpers
  py.typed               # PEP 561 marker: this package ships type hints
examples/                # copy-paste usage examples
tests/                   # mocked API tests
```

`py.typed` is intentionally empty. Its only job is to tell tools like mypy,
Pyright, and modern editors that `prysmatic_sdk` should be treated as a typed
package when users import it.

## REST quickstart

```python
from prysmatic_sdk import PrysmaticClient

client = PrysmaticClient(api_key="prys_...")

wallets = client.wallets.list(page=1)
print(wallets.total)

metrics = client.wallets.metrics("W12")
print(metrics.identity.score, metrics.behavior.winrate)

holdings = client.wallets.holdings("W12")
for item in holdings.tokens:
    print(item.token.address, item.position.balance)

coheld = client.tokens.held(min_wallets=3)
for item in coheld.items:
    print(item.token.address, item.holders.wallet_count)

flow = client.tokens.swaps(
    "FSA7iqBeeENna2LUmZyqCYce7op2jBc9ztXLKdM6bonk",
    aggregate=True,
)
print(flow.tracked_wallets)

client.close()
```

You can also use the client as a context manager:

```python
from prysmatic_sdk import PrysmaticClient

with PrysmaticClient(api_key="prys_...") as client:
    wallets = client.wallets.list()
```

## Async REST

```python
import asyncio
from prysmatic_sdk import AsyncPrysmaticClient

async def main() -> None:
    async with AsyncPrysmaticClient(api_key="prys_...") as client:
        wallets = await client.wallets.list(page=1)
        print(wallets.total)

asyncio.run(main())
```

## Live trades

```python
import asyncio
from prysmatic_sdk import AsyncPrysmaticClient

async def main() -> None:
    async with AsyncPrysmaticClient(api_key="prys_...") as client:
        async for trade in client.stream.trades(wallets=["W12", "W37"]):
            print(
                trade.data.wallet,
                trade.data.side,
                trade.data.mint,
                trade.data.sol_amount,
            )

asyncio.run(main())
```

The stream client:

- authenticates to `/ws` with `Authorization: Bearer <API_KEY>`
- resubscribes after reconnecting
- applies exponential backoff with jitter
- ignores free heartbeat pings
- raises typed errors for exhausted balance and superseded connections

## Error handling

```python
from prysmatic_sdk import (
    InsufficientCreditsError,
    PrysmaticClient,
    RateLimitedError,
    UnauthorizedError,
)

client = PrysmaticClient(api_key="prys_...")

try:
    wallets = client.wallets.list()
except UnauthorizedError:
    print("Bad or missing API key")
except InsufficientCreditsError:
    print("Top up credits before retrying")
except RateLimitedError:
    print("Back off and retry later")
```

## Configuration

```python
client = PrysmaticClient(
    api_key="prys_...",
    base_url="https://api.prysmatic-sol.xyz",
    timeout=20.0,
)
```

For local development:

```python
client = PrysmaticClient(
    api_key="dev-key",
    base_url="http://127.0.0.1:8090",
)
```

The async WebSocket client derives `ws://` or `wss://` from `base_url`. You can
override it:

```python
client = AsyncPrysmaticClient(
    api_key="prys_...",
    base_url="https://api.prysmatic-sol.xyz",
    ws_url="wss://api.prysmatic-sol.xyz/ws",
)
```

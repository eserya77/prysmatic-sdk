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


if __name__ == "__main__":
    asyncio.run(main())

from prysmatic_sdk import PrysmaticClient


def main() -> None:
    client = PrysmaticClient(api_key="prys_...")
    try:
        wallets = client.wallets.list(page=1)
        print(f"tracked wallets: {wallets.total}")

        if wallets.items:
            alias = wallets.items[0].identity.wallet
            metrics = client.wallets.metrics(alias)
            print(f"{alias} score: {metrics.identity.score}")
    finally:
        client.close()


if __name__ == "__main__":
    main()

import requests


def convert_usdt_to_crypto(amount_usdt, target_crypto):
    crypto_ids = {
        "USDT": "tether",
        "ETH": "ethereum",
        "LTC": "litecoin",
        "BTC": "bitcoin",
        "BNB": "binancecoin",
    }
    if target_crypto not in crypto_ids:
        raise ValueError("Указанная криптовалюта не поддерживается или не найдена.")
    if target_crypto == "USDT":
        return amount_usdt
    crypto_id = crypto_ids[target_crypto]
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    )
    data = response.json()
    if crypto_id in data:
        crypto_price_in_usd = data[crypto_id]["usd"]
        return amount_usdt / crypto_price_in_usd
    else:
        raise ValueError("Не удалось получить данные о цене выбранной криптовалюты.")

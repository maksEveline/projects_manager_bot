import json


def get_fixed_prices():
    with open("fixed_prices.json", "r") as file:
        return json.load(file)

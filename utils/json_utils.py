import json


def get_fixed_prices():
    with open("fixed_prices.json", "r") as file:
        return json.load(file)


def get_settings():
    with open("settings.json", "r") as file:
        return json.load(file)


def get_project_percentage():
    with open("settings.json", "r") as file:
        return json.load(file)["project_percentage"]


def get_price_per_project():
    with open("settings.json", "r") as file:
        return json.load(file)["price_per_project"]


def set_project_percentage(percentage: float):
    with open("settings.json", "r") as file:
        data = json.load(file)
    data["project_percentage"] = percentage
    with open("settings.json", "w") as file:
        json.dump(data, file)


def set_support_link(link: str):
    with open("settings.json", "r") as file:
        data = json.load(file)
    data["support_link"] = link
    with open("settings.json", "w") as file:
        json.dump(data, file)


def set_update_channel_link(link: str):
    with open("settings.json", "r") as file:
        data = json.load(file)
    data["update_channel_link"] = link
    with open("settings.json", "w") as file:
        json.dump(data, file)


def set_price_per_project(price: int):
    with open("settings.json", "r") as file:
        data = json.load(file)
    data["price_per_project"] = price
    with open("settings.json", "w") as file:
        json.dump(data, file)


def update_project_prices(count: int, price: int) -> bool:
    try:
        with open("fixed_prices.json", "r") as file:
            data = json.load(file)

            for item in data:
                if item["count"] == count:
                    item["price"] = int(price)
                    break
            else:
                data.append({"count": count, "price": int(price)})
                data.sort(key=lambda x: x["count"])

        with open("fixed_prices.json", "w") as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as ex:
        print(ex)
        return False


def get_news_channel_id():
    with open("settings.json", "r") as file:
        return json.load(file)["update_channel_id"]


def set_news_channel_id(id: str):
    with open("settings.json", "r") as file:
        data = json.load(file)
    data["update_channel_id"] = id
    with open("settings.json", "w") as file:
        json.dump(data, file)

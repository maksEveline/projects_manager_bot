import json


def get_fixed_prices():
    with open("fixed_prices.json", "r") as file:
        return json.load(file)


def get_project_percentage():
    with open("settings.json", "r") as file:
        return json.load(file)["project_percentage"]


def set_project_percentage(percentage: float):
    with open("settings.json", "w") as file:
        json.dump({"project_percentage": percentage}, file)

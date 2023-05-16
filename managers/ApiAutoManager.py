import requests
import json

class ApiAutoManager:
    def __init__(self, config):
        self.search_url = config["searchUrl"]
        self.info_url = config["infoUrl"]
        self.avg_price_url = config["avgPriceUrl"]
        self.api_key = config["key"]

    def get_search_data(self, search_params):
        url = f"{self.search_url}?{search_params}&top=1&api_key={self.api_key}"
        print(url)
        response = requests.get(url)
        data = json.loads(response.text)
        return data

    def get_car_data(self, announcement_id):
        url = f"{self.info_url}?api_key={self.api_key}&auto_id={announcement_id}"
        response = requests.get(url)
        data = json.loads(response.text)
        return data

    def get_avg_price(self, announcement_data):
        if (announcement_data['autoData']['year'] + round(announcement_data['autoData']['year'] * 0.0015)) > 2023:
            to_year = 2023
        else:
            to_year = announcement_data['autoData']['year'] + round(announcement_data['autoData']['year'] * 0.0015)

        url = f"{self.avg_price_url}?api_key={self.api_key}&marka_id={announcement_data['markId']}" \
              f"&model_id={announcement_data['modelId']}" \
              f"&raceInt={announcement_data['autoData']['raceInt'] - round(announcement_data['autoData']['raceInt'] * 0.2)}" \
              f"&raceInt={announcement_data['autoData']['raceInt'] + round(announcement_data['autoData']['raceInt'] * 0.2)}" \
              f"&yers={announcement_data['autoData']['year'] - round(announcement_data['autoData']['year'] * 0.0015)}&yers={to_year}"
        response =  requests.get(url)
        data = json.loads(response.text)
        return data

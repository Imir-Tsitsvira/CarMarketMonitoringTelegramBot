import requests
import json

class ApiAutoManager:
    def __init__(self, config):
        self.search_url = config["searchUrl"]
        self.info_url = config["infoUrl"]
        self.avg_price_url = config["avgPriceUrl"]
        self.api_key = config["key"]

    def get_search_data(self, search_params):
        data = 0
        return data

    def get_car_data(self, announcement_id):
        data = 0
        return data

    def get_avg_price(self, announcement_data):
        data = 0
        return data

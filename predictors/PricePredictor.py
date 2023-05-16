import re

import joblib
import pandas as pd


class PricePredictor:

    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def predict_price(self, data):
        engine_data = re.split(', ', data["autoData"]["fuelName"])
        fuel_type = engine_data[0]
        engine_volume_match = re.search('\d+(\.\d+)?', engine_data[1])
        if engine_volume_match is not None:
            engine_volume = engine_volume_match.group()
        else:
            engine_volume = 2

        car_data = {"brand": data["markName"],
                    "model": data["modelName"],
                    "fuel_type": fuel_type,
                    "transmission_type": data["autoData"]["gearboxName"],
                    "year": data["autoData"]["year"],
                    "mileage": data["autoData"]["raceInt"],
                    "engine_volume": engine_volume,
                    "owners": 2
        }

        print(data["autoData"]["fuelName"])
        df = pd.DataFrame([car_data])
        prediction = self.model.predict(df)

        return prediction[0]



    def load_model(self, model_path):
        return joblib.load(model_path)
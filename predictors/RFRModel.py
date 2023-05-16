from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib
import json
import os

class Model:
    def __init__(self):
        self.categorical_features = ["brand", "model", "fuel_type", "transmission_type"]
        self.numeric_features = ["year", "mileage", "engine_volume", "owners"]


    def set_train_data(self, file_path):
        data_frame = pd.read_csv(file_path)
        return data_frame

    def load_hyperparams(self):
        with open('./data/models/params/best_params.json', "r") as file:
            data = json.load(file)
        return data

    def save_hyperparams(self, data):
        with open('./data/models/params/best_params.json', 'w') as file:
            file.write(json.dumps(data))

    def load_model(model_path):
        return joblib.load(model_path)

    def save_model(self, model, model_path):
        return joblib.dump(model, model_path)

    def train(self, pipeline, splited_df):
        data = self.hyperparams()
        params = data["params"]
        model = pipeline.set_params(**params)
        model.fit(splited_df["X_train"], splited_df["Y_train"])
        print(pipeline.score(splited_df["X_test"], splited_df["Y_test"]))
        return model

    def tune_hyperparams(self, pipeline, splitted_data_frame):
        param_grid = {
            "regressor__n_estimators": [25, 50, 75,100],
            "regressor__max_depth": [None, 15, 30, 45, 60],
            "regressor__min_samples_split": [10, 15, 20],
            "regressor__min_samples_leaf": [3, 5, 7],
            "regressor__max_features": ['auto', 'sqrt', 'log2'],
            "regressor__bootstrap": [True, False]
        }

        grid_search = GridSearchCV(
            pipeline,
            param_grid,
            cv=5,
            scoring="neg_mean_squared_error",
            verbose=1,
            n_jobs=os.cpu_count() - 3)

        grid_search.fit(splitted_data_frame["X_train"], splitted_data_frame["Y_train"])
        to_json = {'params': grid_search.best_params_}
        self.save_hyperparams(to_json)

        return grid_search.score(splitted_data_frame["X_test"], splitted_data_frame["Y_test"])


    def pipeline(self):
        feature_transformer = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self.numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), self.categorical_features),
            ]
        )
        model = RandomForestRegressor()
        pipeline = Pipeline([("preprocessor", feature_transformer), ("regressor", model)])
        return pipeline

    def splite_data_frame(self, data_frame):
        X = data_frame.drop(columns=["price"])
        Y = data_frame["price"]
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, testsize=0.2, random_state=42)

        splitted_data_frame = {
            "X_train": X_train, "Y_train": Y_train,
            "X_test": X_test, "Y_test": Y_test
        }
        return splitted_data_frame

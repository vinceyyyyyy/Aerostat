import json
import os
import pickle

import pandas as pd


def predict(model_path: str, data: dict, input_columns: list[str]) -> dict:
    """
    :param model_path: path to the model file
    :param data: {column_1: [value1, value2, ...], column_2: [value1, value2, ...], ...}
    :param input_columns: list of columns to be used as input
    :return: {column_1: [value1, value2, ...], column_2: [value1, value2, ...], ...}
    """
    # load model file
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    with open(model_path, "rb") as f:
        try:
            model = pickle.load(f)
            print("Model loaded")
        except Exception as e:
            raise RuntimeError(f"Loading model failed: {e}")

    # load input columns
    if not isinstance(input_columns, list):
        raise ValueError("Input columns must be a list")

    # Run prediction
    df = pd.DataFrame(data)
    prediction_result = model.predict(pd.DataFrame(data)[input_columns])

    # if only one column is returned, name it as result
    prediction_df = pd.DataFrame(prediction_result)
    if prediction_df.shape[1] == 1:
        prediction_df.columns = ["result"]

    total_result = pd.concat([df.drop(columns=input_columns), prediction_df], axis=1)

    # Attach unused columns to result. Most likely those are used as id.
    response_body = total_result.to_dict(orient="list")

    return {"statusCode": 200, "body": json.dumps(response_body)}

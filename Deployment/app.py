from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

model = joblib.load("../Models/trained_stacking_model.pkl")
model_columns = joblib.load("../Models/model_columns.pkl")


def preprocess_input(custom_input):
    """
    Perform feature engineering and preprocessing on the input data.
    """
    df_input = pd.DataFrame([custom_input])

    # Feature Engineering
    df_input['is_top_floor'] = df_input['current_floor'] == df_input['total_from']
    df_input['is_first_floor'] = df_input['current_floor'] == 1
    df_input['is_old_building'] = df_input['building_type'].apply(lambda x: 1 if x == 'old' else 0)
    df_input['bill_of_sale'] = df_input['bill_of_sale'].apply(lambda x: 1 if x == 'Yes' else 0)
    df_input['repair_status_encoded'] = df_input['repair_status'].apply(
        lambda x: 1 if x == 'Yes' else 0)
    df_input['room_area_ratio'] = df_input['room_size'] / df_input['area']
    df_input['area_room_ratio'] = df_input['area'] / df_input['room_size']
    df_input['floor_density'] = df_input['current_floor'] / (df_input['total_from'] + 1)
    df_input["area_floor_density"] = df_input["area"] * df_input["floor_density"]
    df_input["top_old_building"] = df_input["is_top_floor"] * df_input["is_old_building"]
    df_input["log_total_floors"] = np.log1p(df_input["total_from"])
    df_input["log_area_floor_density"] = np.log1p(df_input["area_floor_density"])
    df_input["floor_density_squared"] = df_input["floor_density"] ** 2

    # One-hot encoding for categorical columns
    df_input = pd.get_dummies(df_input,
                              columns=['Location1', 'Location2', 'building_type', 'repair_status'],
                              drop_first=True)

    df_input = df_input.reindex(columns=model_columns, fill_value=0)

    return df_input


@app.route('/predict', methods=['POST'])
def predict():
    try:
        custom_input = request.get_json()  # Get JSON data from request
        df_input = preprocess_input(custom_input)

        prediction = int(round(model.predict(df_input)[0], -2))
        return jsonify({"predicted_price": prediction})  # Return result as JSON

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

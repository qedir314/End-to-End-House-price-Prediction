from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
from flask_cors import CORS
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')


class LocationProcessor:
    def __init__(self, csv_path='..//.//Data/raw_data1.csv'):
        # Read CSV once and cache the data
        self.df = pd.read_csv(csv_path)

    def get_location1_options(self):
        # Get unique Location1 values, properly capitalized
        return sorted(self.df['Location1'].str.title().unique().tolist())

    def get_location2_options(self, location1):
        # Filter Location2 options for specific Location1
        filtered_locations = self.df[
            self.df['Location1'].str.lower() == location1.lower()
            ]['Location2'].str.title().unique().tolist()

        return sorted(filtered_locations)


app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir)
CORS(app)

model = joblib.load("../Models/random_forest_model.pkl")
model_columns = joblib.load("../Models/random_forest_columns.pkl")


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

# Serve the frontend
@app.route("/")
def index():
    return render_template("index.html")  # Loads the frontend

@app.route('/predict', methods=['POST'])
def predict():
    try:
        custom_input = request.get_json()  # Get JSON data from request
        df_input = preprocess_input(custom_input)

        prediction = int(round(model.predict(df_input)[0], -2))
        return jsonify({"predicted_price": prediction})  # Return result as JSON

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/get_locations')
def get_locations():
    # Add print statements for debugging
    print("Location Request Received")
    processor = LocationProcessor()

    location1 = request.args.get('location1', '')
    print(f"Received location1: {location1}")

    if not location1:
        location1_options = processor.get_location1_options()
        print(f"Location1 Options: {location1_options}")
        return jsonify({
            'location1_options': location1_options
        })
    else:
        location2_options = processor.get_location2_options(location1)
        print(f"Location2 Options for {location1}: {location2_options}")
        return jsonify({
            'location2_options': location2_options
        })


if __name__ == '__main__':
    app.run(debug=True)

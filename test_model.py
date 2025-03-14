import joblib
import pandas as pd
import numpy as np

# Load the saved model and encoders
model = joblib.load("Models/trained_stacking_model.pkl")
print("Model loaded successfully!")

# Load feature names used during training
model_columns = joblib.load("Models/model_columns.pkl")

# Custom input (raw data)
custom_input = {
    "Location1": "absheron",
    "Location2": "xirdalan",
    "room_size": 2,
    "area": 45,
    "current_floor": 1,
    "total_from": 11,
    "building_type": "new",
    "repair_status": "Yes",
    "bill_of_sale": 'Yes',  # Make sure this is the same
}

# Convert input to DataFrame
df_input = pd.DataFrame([custom_input])

# Feature engineering (replicate preprocessing steps)
df_input['is_top_floor'] = df_input['current_floor'] == df_input['total_from']
df_input['is_first_floor'] = df_input['current_floor'] == 1
df_input['is_old_building'] = df_input['building_type'].apply(lambda x: 1 if x == 'old' else 0)
df_input['bill_of_sale'] = df_input['bill_of_sale'].apply(lambda x: 1 if x == 'Yes' else 0)
df_input['repair_status_encoded'] = df_input['repair_status'].apply(lambda x: 1 if x == 'Yes' else 0)
df_input['room_area_ratio'] = df_input['room_size'] / df_input['area']
df_input['area_room_ratio'] = df_input['area'] / df_input['room_size']
df_input['floor_density'] = df_input['current_floor'] / (df_input['total_from'] + 1)
df_input["area_floor_density"] = df_input["area"] * df_input["floor_density"]
df_input["top_old_building"] = df_input["is_top_floor"] * df_input["is_old_building"]
df_input["log_total_floors"] = np.log1p(df_input["total_from"])
df_input["log_area_floor_density"] = np.log1p(df_input["area_floor_density"])
df_input["floor_density_squared"] = df_input["floor_density"] ** 2

# One-hot encoding for categorical columns
df_input = pd.get_dummies(df_input, columns=['Location1', 'Location2', 'building_type', 'repair_status'], drop_first=True)

# Ensure the input data has the same columns as the training data
df_input = df_input.reindex(columns=model_columns, fill_value=0)

# Predict house price
predicted_price = model.predict(df_input)[0]

print(f"🏠 Predicted Price: {predicted_price:,.2f} AZN")

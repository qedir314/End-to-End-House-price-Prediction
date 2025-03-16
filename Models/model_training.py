import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np

# Load the processed dataset
df = pd.read_csv("../Data/processed_data.csv")

X = df.drop(columns=["price (AZN)"])  # Drop target column
y = df["price (AZN)"]  # Target variable

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create RandomForestRegressor with predefined parameters
rf_model = RandomForestRegressor(random_state=42)

# Train the model
rf_model.fit(X_train, y_train)

# Predictions
y_pred = rf_model.predict(X_test)

# Evaluation Metrics
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"R² Score: {r2:.4f}")
print(f"Root Mean Squared Error: {rmse:.4f}")

# Save the model
joblib.dump(rf_model, "../Models/random_forest_model.pkl", compress=True)

# Save model columns
joblib.dump(list(X.columns), "../Models/random_forest_columns.pkl")

print("Model training complete!")

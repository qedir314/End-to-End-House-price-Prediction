import pandas as pd
import joblib
from sklearn.ensemble import StackingRegressor, RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# Load the processed dataset
df = pd.read_csv("../Data/processed_data.csv")

X = df.drop(columns=["price (AZN)"])  # Drop target column
y = df["price (AZN)"]  # Target variable

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model_columns = list(X_train.columns)

base_models = [
    ('Linear Regression', LinearRegression()),
    ('Decision Tree', DecisionTreeRegressor(random_state=42)),
    ('Random Forest', RandomForestRegressor(
    n_estimators=275,
    min_samples_split=5,
    min_samples_leaf=1,
    max_features="sqrt",
    max_depth=15,
    random_state=42)),
    ('Gradient Boosting', GradientBoostingRegressor(random_state=42)),
    ('XGBRegressor', XGBRegressor(random_state=42)),
    ('KNeighborsRegressor', KNeighborsRegressor()),
    ('AdaBoostRegressor', AdaBoostRegressor(random_state=42))
]

accuracy_scores = []
for model in base_models:
    model[1].fit(X_train, y_train)
    y_pred = model[1].predict(X_test)
    accuracy_scores.append((model[0], r2_score(y_test, y_pred)))

print("Base models trained successfully.")

# Select models with R2 score > 0.80
best_models = [(name, model) for (name, model), score in zip(base_models, accuracy_scores) if
               score[1] > 0.80]

stacking_model = StackingRegressor(
    estimators=best_models,
    final_estimator=RandomForestRegressor(random_state=42),
    cv=5
)

# Train stacking model
stacking_model.fit(X_train, y_train)
print("Stacking model training complete.")
print("R2 score:", stacking_model.score(X_test, y_test))

# Save the trained model
joblib.dump(stacking_model, "../Models/trained_stacking_model.pkl", compress=True)

print("Model training complete. Saved as '../Models/trained_stacking_model.pkl'.")

# Save model columns
joblib.dump(model_columns, "model_columns.pkl")
print("Saved model columns successfully!")
